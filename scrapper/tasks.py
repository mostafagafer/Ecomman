from celery import shared_task
# from client_profile.models import Profile  # Ensure this import matches the app where Profile is located
from .models import Product, ScrapedData, ScrapedBulkData
# from .selenium_codes.Scrapper_functions import scrape_prices_from_dawa, scrape_prices_from_nahdi, scrape_prices_from_amazon 
from .selenium_codes.Requests_functions import *
from .selenium_codes.Requests_functions_Bulk import *
import random
# import psutil
# import time
import logging
# import aiohttp
import asyncio

logger = logging.getLogger(__name__)


# Scheduled tasks
@shared_task
def scheduled_products_scraper(sample_size=200):
    try:
        # Fetch all products
        all_products = Product.objects.all()
        
        # Select a random sample of products
        if all_products.count() > sample_size:
            products = random.sample(list(all_products), sample_size)
        else:
            products = all_products
        
        records_to_create = []
        records_created = 0
        
        loop = asyncio.get_event_loop()
        for product in products:
            dawa_id = [link.identifier for link in product.account_id_links.filter(account_id__name='dawa')]
            nahdi_id = [link.identifier for link in product.account_id_links.filter(account_id__name='nahdi')]
            amazon_id = [link.identifier for link in product.account_id_links.filter(account_id__name='amazon')]
            noon_sa_id = [link.identifier for link in product.account_id_links.filter(account_id__name='noon_sa')]


            # Amazon processing
            try:
                # Fetch data from Amazon
                amazon_titles, amazon_prices, amazon_shipping, amazon_sold, amazon_availability, amazon_discount, amazon_sold_count, amazon_choice = (
                    loop.run_until_complete(get_amazon_product_details(amazon_id)) if amazon_id else
                    ([None], [None], [None], [None], [None], [None], [None], [None])
                )
                logger.info(f"Amazon data: {amazon_titles}, {amazon_prices}, {amazon_shipping}, {amazon_sold}, {amazon_availability}, {amazon_discount}, {amazon_sold_count}, {amazon_choice}")

            except Exception as e:
                logger.error(f"Error fetching Amazon details: {e}")
                amazon_titles, amazon_prices, amazon_shipping, amazon_sold, amazon_availability, amazon_discount, amazon_sold_count, amazon_choice = [None] * 8

            # Dawa processing
            try:
                # Fetch data from Dawa
                dawa_data = loop.run_until_complete(get_dawa_prices(dawa_id)) if dawa_id else [{}]

                if isinstance(dawa_data, list) and dawa_data:
                    dawa_titles = [item.get('name') for item in dawa_data]
                    dawa_prices = [item.get('price') for item in dawa_data]
                    dawa_availability_info = [item.get('availability_info') for item in dawa_data]
                    dawa_original_prices = [item.get('price_original') for item in dawa_data]
                    dawa_is_in_stock_msi = [item.get('is_in_stock_msi') for item in dawa_data]
                    dawa_offer_text = [item.get('offer_text_notag') for item in dawa_data]
                    dawa_discount = [item.get('discount') for item in dawa_data]
                else:
                    dawa_titles, dawa_prices, dawa_availability_info, dawa_original_prices, dawa_is_in_stock_msi, dawa_offer_text, dawa_discount = [None] * 7

                logger.info(f"Dawa data: {dawa_titles}, {dawa_prices}, {dawa_availability_info}, {dawa_original_prices}, {dawa_is_in_stock_msi}, {dawa_offer_text}, {dawa_discount}")

            except Exception as e:
                logger.error(f"Error fetching Dawa details: {e}")
                dawa_titles, dawa_prices, dawa_availability_info, dawa_original_prices, dawa_is_in_stock_msi, dawa_offer_text, dawa_discount = [None] * 7

            # Nahdi processing
            try:
                # Fetch data from Nahdi
                nahdi_data = loop.run_until_complete(get_nahdi_prices(nahdi_id)) if nahdi_id else [{}]

                if isinstance(nahdi_data, list) and nahdi_data:
                    nahdi_titles = [item.get('name') for item in nahdi_data]
                    nahdi_prices = [item.get('price') for item in nahdi_data]
                    nahdi_availability_info = [item.get('availability_info') for item in nahdi_data]
                    nahdi_original_prices = [item.get('price_original') for item in nahdi_data]
                    nahdi_ordered_qty = [item.get('ordered_qty') for item in nahdi_data]
                    nahdi_sold_out = [item.get('sold_out') for item in nahdi_data]
                    nahdi_limited_stock = [item.get('limited_stock') for item in nahdi_data]
                    nahdi_discount = [item.get('discount') for item in nahdi_data]
                else:
                    nahdi_titles, nahdi_prices, nahdi_availability_info, nahdi_original_prices, nahdi_ordered_qty, nahdi_sold_out, nahdi_limited_stock, nahdi_discount = [None] * 8

                logger.info(f"Nahdi data: {nahdi_titles}, {nahdi_prices}, {nahdi_availability_info}, {nahdi_original_prices}, {nahdi_ordered_qty}, {nahdi_sold_out}, {nahdi_limited_stock}, {nahdi_discount}")

            except Exception as e:
                logger.error(f"Error fetching Nahdi details: {e}")
                nahdi_titles, nahdi_prices, nahdi_availability_info, nahdi_original_prices, nahdi_ordered_qty, nahdi_sold_out, nahdi_limited_stock, nahdi_discount = [None] * 8

            # Noon processing
            try:
                # Fetch data from Noon
                noon_data = loop.run_until_complete(get_noon_prices(noon_sa_id)) if noon_sa_id else [{}]

                # Process fetched Noon data
                if isinstance(noon_data, list) and noon_data:
                    noon_titles = [item.get('product_name') for item in noon_data]
                    noon_prices = [item.get('current_price') for item in noon_data]
                    noon_availability_info = [item.get('is_buyable') for item in noon_data]
                    noon_original_prices = [item.get('original_price') for item in noon_data]
                    noon_sold_by = [item.get('sold_by', None) for item in noon_data]  # Optional field
                    noon_discount = [item.get('discount', None) for item in noon_data]  # Optional field
                else:
                    noon_titles, noon_prices, noon_availability_info, noon_original_prices, noon_sold_by, noon_discount = [None] * 6

                logger.info(f"Noon data: {noon_titles}, {noon_prices}, {noon_availability_info}, {noon_original_prices}, {noon_sold_by},  {noon_discount}")

            except Exception as e:
                logger.error(f"Error fetching Noon details: {e}")
                noon_titles, noon_prices, noon_availability_info, noon_original_prices, noon_sold_by, noon_discount = [None] * 6


            # Assign extracted values
            price_dawa = dawa_prices[0] if dawa_prices else None
            title_dawa = dawa_titles[0] if dawa_titles else None
            availability_dawa = dawa_availability_info[0] if dawa_availability_info else None
            original_price_dawa = dawa_original_prices[0] if dawa_original_prices else None
            is_in_stock_dawa = dawa_is_in_stock_msi[0] if dawa_is_in_stock_msi else None
            offer_text_dawa = dawa_offer_text[0] if dawa_offer_text else None
            discount_dawa = dawa_discount[0] if dawa_discount else None

            price_nahdi = nahdi_prices[0] if nahdi_prices else None
            title_nahdi = nahdi_titles[0] if nahdi_titles else None
            availability_nahdi = nahdi_availability_info[0] if nahdi_availability_info else None
            original_price_nahdi = nahdi_original_prices[0] if nahdi_original_prices else None
            ordered_qty_nahdi = nahdi_ordered_qty[0] if nahdi_ordered_qty else None
            sold_out_nahdi = nahdi_sold_out[0] if nahdi_sold_out else None
            limited_stock_nahdi = nahdi_limited_stock[0] if nahdi_limited_stock else None
            discount_nahdi = nahdi_discount[0] if nahdi_discount else None

            price_amazon = amazon_prices[0] if amazon_prices else None
            ship_amazon = amazon_shipping[0] if amazon_shipping else None
            sold_amazon = amazon_sold[0] if amazon_sold else None
            title_amazon = amazon_titles[0] if amazon_titles else None
            availability_amazon = amazon_availability[0] if amazon_availability else None
            discount_amazon = amazon_discount[0] if amazon_discount else None
            sold_count_amazon = amazon_sold_count[0] if amazon_sold_count else None
            amazon_choice_badge = bool(amazon_choice[0]) if amazon_choice else False


            # Assign extracted values for the first record
            price_noon = noon_prices[0] if noon_prices else None
            original_price_noon = noon_original_prices[0] if noon_original_prices else None
            title_noon = noon_titles[0] if noon_titles else None
            availability_noon = noon_availability_info[0] if noon_availability_info else None
            sold_noon = noon_sold_by[0] if noon_sold_by else None
            discount_noon = noon_discount[0] if noon_discount else None

            # Log and create ScrapedData record
            records_to_create.append(ScrapedData(
                product=product,
                dawa_price=price_dawa,
                dawa_title=title_dawa,
                dawa_availability_info=availability_dawa,
                dawa_original_price=original_price_dawa,
                dawa_is_in_stock_msi=is_in_stock_dawa,
                dawa_offer_text_notag=offer_text_dawa,
                dawa_discount = discount_dawa,
                
                nahdi_price=price_nahdi,
                nahdi_title=title_nahdi,
                nahdi_availability_info=availability_nahdi,
                nahdi_original_price=original_price_nahdi,
                nahdi_ordered_qty=ordered_qty_nahdi,
                nahdi_sold_out=sold_out_nahdi,
                nahdi_limited_stock=limited_stock_nahdi,
                nahdi_discount = discount_nahdi,
                
                amazon_price=price_amazon,
                amazon_shipping=ship_amazon,
                amazon_sold_by=sold_amazon,
                amazon_title=title_amazon,
                amazon_availability_info=availability_amazon,
                amazon_discount=discount_amazon,
                amazon_sold_count=sold_count_amazon,
                amazon_choice=amazon_choice_badge,
                
                noon_sa_price=price_noon,
                noon_sa_title=title_noon,
                noon_sa_availability_info=availability_noon,
                noon_sa_original_price=original_price_noon,
                noon_sa_sold_by=sold_noon,
                noon_sa_discount = discount_noon,

            ))
            records_created += 1

        # Bulk create ScrapedData entries
        ScrapedData.objects.bulk_create(records_to_create)

        return {
            'status': 'success',
            'total_products': len(products),
            'records_created': records_created
        }
    
    except Exception as e:
        # Log the error and return error details if an exception occurs
        logger.error(f"Error in scrape_user_products_task: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }

@shared_task
def scheduled_bulk_scraper(sample_size=200):
    try:
        # Fetch all products
        all_products = Product.objects.all()
        
        # Select a random sample of products
        if all_products.count() > sample_size:
            products = random.sample(list(all_products), sample_size)
        else:
            products = all_products
        
        records_to_create = []
        records_created = 0
        loop = asyncio.get_event_loop()

        # Initialize a dictionary for collecting all queries
        all_queries = {}

        # Collect unique queries across all products
        for product in products:
            if product.category:
                all_queries[product.category.name] = 20  # Use 20 for category
            if product.subcategory:
                all_queries[product.subcategory.name] = 10  # Use 10 for subcategory

        # Extract unique queries and their corresponding num_products
        unique_queries = list(all_queries.keys())
        num_products_list = [all_queries[query] for query in unique_queries]

        # Fetch data from Amazon
        try:
            amazon_data = [
                loop.run_until_complete(get_amazon_details([query], num_products))
                for query, num_products in zip(unique_queries, num_products_list)
            ]
            # Flatten the list of amazon_data results
            amazon_data = [item for sublist in amazon_data for item in sublist]
        except Exception as e:
            logger.error(f"Error fetching data from Amazon: {str(e)}")
            amazon_data = []

        # Fetch data from Dawa 
        try:
            dawa_data = [
                loop.run_until_complete(get_dawa_details([query], num_products))
                for query, num_products in zip(unique_queries, num_products_list)
            ]
            # Flatten the list of dawa_data results
            dawa_data = [item for sublist in dawa_data for item in sublist]
        except Exception as e:
            logger.error(f"Error fetching data from Dawa: {str(e)}")
            dawa_data = []

        # Fetch data from  Nahdi
        try:
            nahdi_data = [
                loop.run_until_complete(get_nahdi_details([query], num_products))
                for query, num_products in zip(unique_queries, num_products_list)
            ]
            # Flatten the list of nahdi_data results
            nahdi_data = [item for sublist in nahdi_data for item in sublist]
        except Exception as e:
            logger.error(f"Error fetching data from Nahdi: {str(e)}")
            nahdi_data = []

        # Fetch data from  Noon
        try:
            noon_data = [
                loop.run_until_complete(get_noon_details([query], num_products))
                for query, num_products in zip(unique_queries, num_products_list)
            ]
            # Flatten the list of nahdi_data results
            noon_data = [item for sublist in noon_data for item in sublist]
        except Exception as e:
            logger.error(f"Error fetching data from Noon: {str(e)}")
            noon_data = []

        # Process the Dawa fetched data and append to records_to_create
        for entry in dawa_data:
            records_to_create.append(ScrapedBulkData(
                key_name=entry['key'],  # Either category or subcategory name
                dawa_price=entry['price'],
                dawa_title=entry['name'],
                dawa_original_price=entry['price_original'],
                dawa_offer_text_notag=entry['offer_text_notag'],
                dawa_sku=entry['sku'],
                dawa_discount=entry['discount'],
            ))
            records_created += 1

        # Process the Nahdi fetched data and append to records_to_create
        for entry in nahdi_data:
            records_to_create.append(ScrapedBulkData(
                key_name=entry['key'],  # Either category or subcategory name
                nahdi_price=entry['price'],
                nahdi_title=entry['name'],
                nahdi_original_price=entry['price_original'],
                nahdi_ordered_qty=entry['ordered_qty'],
                nahdi_sku=entry['sku'],
                nahdi_discount=entry['discount'],
            ))
            records_created += 1

        # Process the Amazon fetched data and append to records_to_create
        for entry in amazon_data:
            records_to_create.append(ScrapedBulkData(
                key_name=entry['key'],  # Either category or subcategory name
                amazon_price=entry['current_price'],
                amazon_title=entry['title'],
                amazon_original_price=entry['original_price'],
                amazon_sku=entry['ASIN'],
                amazon_discount=entry['amazon_discount'],
                # amazon_purchase_count=entry['purchase_count'],
            ))
            records_created += 1


        # Process the Noon fetched data and append to records_to_create
        for entry in noon_data:
            records_to_create.append(ScrapedBulkData(
                key_name=entry['key'],  # Either category or subcategory name
                noon_sa_price=entry['price'],
                noon_sa_title=entry['name'],
                noon_sa_original_price=entry['price_original'],
                noon_sa_sku=entry['sku'],
                noon_sa_discount=entry['discount'],
            ))
            records_created += 1

        # Bulk create ScrapedBulkData entries
        ScrapedBulkData.objects.bulk_create(records_to_create)

        return {
            'status': 'success',
            'total_products': len(products),
            'records_created': records_created
        }
    
    except Exception as e:
        logger.error(f"Error in scrape_Bulk_product_task: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }



# Trigerred tasks
@shared_task
def scrape_user_products_task(product_ids):
    try:
        # Fetch the products based on the passed IDs
        products = Product.objects.filter(id__in=product_ids)
        
        records_to_create = []
        records_created = 0
        loop = asyncio.get_event_loop()
        for product in products:
            dawa_id = [link.identifier for link in product.account_id_links.filter(account_id__name='dawa')]
            nahdi_id = [link.identifier for link in product.account_id_links.filter(account_id__name='nahdi')]
            amazon_id = [link.identifier for link in product.account_id_links.filter(account_id__name='amazon')]
            noon_sa_id = [link.identifier for link in product.account_id_links.filter(account_id__name='noon_sa')]


            # Amazon processing
            try:
                # Fetch data from Amazon
                amazon_titles, amazon_prices, amazon_shipping, amazon_sold, amazon_availability, amazon_discount, amazon_sold_count, amazon_choice = (
                    loop.run_until_complete(get_amazon_product_details(amazon_id)) if amazon_id else
                    ([None], [None], [None], [None], [None], [None], [None], [None])
                )
                logger.info(f"Amazon data: {amazon_titles}, {amazon_prices}, {amazon_shipping}, {amazon_sold}, {amazon_availability}, {amazon_discount}, {amazon_sold_count}, {amazon_choice}")

            except Exception as e:
                logger.error(f"Error fetching Amazon details: {e}")
                amazon_titles, amazon_prices, amazon_shipping, amazon_sold, amazon_availability, amazon_discount, amazon_sold_count, amazon_choice = [None] * 8

            # Dawa processing
            try:
                # Fetch data from Dawa
                dawa_data = loop.run_until_complete(get_dawa_prices(dawa_id)) if dawa_id else [{}]

                if isinstance(dawa_data, list) and dawa_data:
                    dawa_titles = [item.get('name') for item in dawa_data]
                    dawa_prices = [item.get('price') for item in dawa_data]
                    dawa_availability_info = [item.get('availability_info') for item in dawa_data]
                    dawa_original_prices = [item.get('price_original') for item in dawa_data]
                    dawa_is_in_stock_msi = [item.get('is_in_stock_msi') for item in dawa_data]
                    dawa_offer_text = [item.get('offer_text_notag') for item in dawa_data]
                    dawa_discount = [item.get('discount') for item in dawa_data]
                else:
                    dawa_titles, dawa_prices, dawa_availability_info, dawa_original_prices, dawa_is_in_stock_msi, dawa_offer_text, dawa_discount = [None] * 7

                logger.info(f"Dawa data: {dawa_titles}, {dawa_prices}, {dawa_availability_info}, {dawa_original_prices}, {dawa_is_in_stock_msi}, {dawa_offer_text}, {dawa_discount}")

            except Exception as e:
                logger.error(f"Error fetching Dawa details: {e}")
                dawa_titles, dawa_prices, dawa_availability_info, dawa_original_prices, dawa_is_in_stock_msi, dawa_offer_text, dawa_discount = [None] * 7

            # Nahdi processing
            try:
                # Fetch data from Nahdi
                nahdi_data = loop.run_until_complete(get_nahdi_prices(nahdi_id)) if nahdi_id else [{}]

                if isinstance(nahdi_data, list) and nahdi_data:
                    nahdi_titles = [item.get('name') for item in nahdi_data]
                    nahdi_prices = [item.get('price') for item in nahdi_data]
                    nahdi_availability_info = [item.get('availability_info') for item in nahdi_data]
                    nahdi_original_prices = [item.get('price_original') for item in nahdi_data]
                    nahdi_ordered_qty = [item.get('ordered_qty') for item in nahdi_data]
                    nahdi_sold_out = [item.get('sold_out') for item in nahdi_data]
                    nahdi_limited_stock = [item.get('limited_stock') for item in nahdi_data]
                    nahdi_discount = [item.get('discount') for item in nahdi_data]
                else:
                    nahdi_titles, nahdi_prices, nahdi_availability_info, nahdi_original_prices, nahdi_ordered_qty, nahdi_sold_out, nahdi_limited_stock, nahdi_discount = [None] * 8

                logger.info(f"Nahdi data: {nahdi_titles}, {nahdi_prices}, {nahdi_availability_info}, {nahdi_original_prices}, {nahdi_ordered_qty}, {nahdi_sold_out}, {nahdi_limited_stock}, {nahdi_discount}")

            except Exception as e:
                logger.error(f"Error fetching Nahdi details: {e}")
                nahdi_titles, nahdi_prices, nahdi_availability_info, nahdi_original_prices, nahdi_ordered_qty, nahdi_sold_out, nahdi_limited_stock, nahdi_discount = [None] * 8

            # Noon processing
            try:
                # Fetch data from Noon
                noon_data = loop.run_until_complete(get_noon_prices(noon_sa_id)) if noon_sa_id else [{}]

                # Process fetched Noon data
                if isinstance(noon_data, list) and noon_data:
                    noon_titles = [item.get('product_name') for item in noon_data]
                    noon_prices = [item.get('current_price') for item in noon_data]
                    noon_availability_info = [item.get('is_buyable') for item in noon_data]
                    noon_original_prices = [item.get('original_price') for item in noon_data]
                    noon_sold_by = [item.get('sold_by', None) for item in noon_data]  # Optional field
                    noon_discount = [item.get('discount', None) for item in noon_data]  # Optional field
                else:
                    noon_titles, noon_prices, noon_availability_info, noon_original_prices, noon_sold_by, noon_discount = [None] * 6

                logger.info(f"Noon data: {noon_titles}, {noon_prices}, {noon_availability_info}, {noon_original_prices}, {noon_sold_by},  {noon_discount}")

            except Exception as e:
                logger.error(f"Error fetching Noon details: {e}")
                noon_titles, noon_prices, noon_availability_info, noon_original_prices, noon_sold_by, noon_discount = [None] * 6


            # Assign extracted values
            price_dawa = dawa_prices[0] if dawa_prices else None
            title_dawa = dawa_titles[0] if dawa_titles else None
            availability_dawa = dawa_availability_info[0] if dawa_availability_info else None
            original_price_dawa = dawa_original_prices[0] if dawa_original_prices else None
            is_in_stock_dawa = dawa_is_in_stock_msi[0] if dawa_is_in_stock_msi else None
            offer_text_dawa = dawa_offer_text[0] if dawa_offer_text else None
            discount_dawa = dawa_discount[0] if dawa_discount else None

            price_nahdi = nahdi_prices[0] if nahdi_prices else None
            title_nahdi = nahdi_titles[0] if nahdi_titles else None
            availability_nahdi = nahdi_availability_info[0] if nahdi_availability_info else None
            original_price_nahdi = nahdi_original_prices[0] if nahdi_original_prices else None
            ordered_qty_nahdi = nahdi_ordered_qty[0] if nahdi_ordered_qty else None
            sold_out_nahdi = nahdi_sold_out[0] if nahdi_sold_out else None
            limited_stock_nahdi = nahdi_limited_stock[0] if nahdi_limited_stock else None
            discount_nahdi = nahdi_discount[0] if nahdi_discount else None

            price_amazon = amazon_prices[0] if amazon_prices else None
            ship_amazon = amazon_shipping[0] if amazon_shipping else None
            sold_amazon = amazon_sold[0] if amazon_sold else None
            title_amazon = amazon_titles[0] if amazon_titles else None
            availability_amazon = amazon_availability[0] if amazon_availability else None
            discount_amazon = amazon_discount[0] if amazon_discount else None
            sold_count_amazon = amazon_sold_count[0] if amazon_sold_count else None
            amazon_choice_badge = bool(amazon_choice[0]) if amazon_choice else False


            # Assign extracted values for the first record
            price_noon = noon_prices[0] if noon_prices else None
            original_price_noon = noon_original_prices[0] if noon_original_prices else None
            title_noon = noon_titles[0] if noon_titles else None
            availability_noon = noon_availability_info[0] if noon_availability_info else None
            sold_noon = noon_sold_by[0] if noon_sold_by else None
            discount_noon = noon_discount[0] if noon_discount else None

            # Log and create ScrapedData record
            records_to_create.append(ScrapedData(
                product=product,
                dawa_price=price_dawa,
                dawa_title=title_dawa,
                dawa_availability_info=availability_dawa,
                dawa_original_price=original_price_dawa,
                dawa_is_in_stock_msi=is_in_stock_dawa,
                dawa_offer_text_notag=offer_text_dawa,
                dawa_discount = discount_dawa,
                
                nahdi_price=price_nahdi,
                nahdi_title=title_nahdi,
                nahdi_availability_info=availability_nahdi,
                nahdi_original_price=original_price_nahdi,
                nahdi_ordered_qty=ordered_qty_nahdi,
                nahdi_sold_out=sold_out_nahdi,
                nahdi_limited_stock=limited_stock_nahdi,
                nahdi_discount = discount_nahdi,
                
                amazon_price=price_amazon,
                amazon_shipping=ship_amazon,
                amazon_sold_by=sold_amazon,
                amazon_title=title_amazon,
                amazon_availability_info=availability_amazon,
                amazon_discount=discount_amazon,
                amazon_sold_count=sold_count_amazon,
                amazon_choice=amazon_choice_badge,
                
                noon_sa_price=price_noon,
                noon_sa_title=title_noon,
                noon_sa_availability_info=availability_noon,
                noon_sa_original_price=original_price_noon,
                noon_sa_sold_by=sold_noon,
                noon_sa_discount = discount_noon,

            ))
            records_created += 1

        # Bulk create ScrapedData entries
        ScrapedData.objects.bulk_create(records_to_create)

        return {
            'status': 'success',
            'total_products': len(products),
            'records_created': records_created
        }
    
    except Exception as e:
        # Log the error and return error details if an exception occurs
        logger.error(f"Error in scrape_user_products_task: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }

@shared_task
def scrape_user_Bulk_product_task(product_ids):
    try:
        # Fetch the products based on the passed IDs
        products = Product.objects.filter(id__in=product_ids)
        
        records_to_create = []
        records_created = 0
        loop = asyncio.get_event_loop()

        # Initialize a dictionary for collecting all queries
        all_queries = {}

        # Collect unique queries across all products
        for product in products:
            if product.category:
                all_queries[product.category.name] = 20  # Use 20 for category
            if product.subcategory:
                all_queries[product.subcategory.name] = 10  # Use 10 for subcategory

        # Extract unique queries and their corresponding num_products
        unique_queries = list(all_queries.keys())
        num_products_list = [all_queries[query] for query in unique_queries]

        # Fetch data from Amazon
        try:
            amazon_data = [
                loop.run_until_complete(get_amazon_details([query], num_products))
                for query, num_products in zip(unique_queries, num_products_list)
            ]
            # Flatten the list of amazon_data results
            amazon_data = [item for sublist in amazon_data for item in sublist]
        except Exception as e:
            logger.error(f"Error fetching data from Amazon: {str(e)}")
            amazon_data = []

        # Fetch data from Dawa 
        try:
            dawa_data = [
                loop.run_until_complete(get_dawa_details([query], num_products))
                for query, num_products in zip(unique_queries, num_products_list)
            ]
            # Flatten the list of dawa_data results
            dawa_data = [item for sublist in dawa_data for item in sublist]
        except Exception as e:
            logger.error(f"Error fetching data from Dawa: {str(e)}")
            dawa_data = []

        # Fetch data from  Nahdi
        try:
            nahdi_data = [
                loop.run_until_complete(get_nahdi_details([query], num_products))
                for query, num_products in zip(unique_queries, num_products_list)
            ]
            # Flatten the list of nahdi_data results
            nahdi_data = [item for sublist in nahdi_data for item in sublist]
        except Exception as e:
            logger.error(f"Error fetching data from Nahdi: {str(e)}")
            nahdi_data = []

        # Fetch data from  Noon
        try:
            noon_data = [
                loop.run_until_complete(get_noon_details([query], num_products))
                for query, num_products in zip(unique_queries, num_products_list)
            ]
            # Flatten the list of nahdi_data results
            noon_data = [item for sublist in noon_data for item in sublist]
        except Exception as e:
            logger.error(f"Error fetching data from Noon: {str(e)}")
            noon_data = []

        # Process the Dawa fetched data and append to records_to_create
        for entry in dawa_data:
            records_to_create.append(ScrapedBulkData(
                key_name=entry['key'],  # Either category or subcategory name
                dawa_price=entry['price'],
                dawa_title=entry['name'],
                dawa_original_price=entry['price_original'],
                dawa_offer_text_notag=entry['offer_text_notag'],
                dawa_sku=entry['sku'],
                dawa_discount=entry['discount'],
            ))
            records_created += 1

        # Process the Nahdi fetched data and append to records_to_create
        for entry in nahdi_data:
            records_to_create.append(ScrapedBulkData(
                key_name=entry['key'],  # Either category or subcategory name
                nahdi_price=entry['price'],
                nahdi_title=entry['name'],
                nahdi_original_price=entry['price_original'],
                nahdi_ordered_qty=entry['ordered_qty'],
                nahdi_sku=entry['sku'],
                nahdi_discount=entry['discount'],
            ))
            records_created += 1

        # Process the Amazon fetched data and append to records_to_create
        for entry in amazon_data:
            records_to_create.append(ScrapedBulkData(
                key_name=entry['key'],  # Either category or subcategory name
                amazon_price=entry['current_price'],
                amazon_title=entry['title'],
                amazon_original_price=entry['original_price'],
                amazon_sku=entry['ASIN'],
                amazon_discount=entry['amazon_discount'],
                # amazon_purchase_count=entry['purchase_count'],
            ))
            records_created += 1


        # Process the Noon fetched data and append to records_to_create
        for entry in noon_data:
            records_to_create.append(ScrapedBulkData(
                key_name=entry['key'],  # Either category or subcategory name
                noon_sa_price=entry['price'],
                noon_sa_title=entry['name'],
                noon_sa_original_price=entry['price_original'],
                noon_sa_sku=entry['sku'],
                noon_sa_discount=entry['discount'],
            ))
            records_created += 1

        # Bulk create ScrapedBulkData entries
        ScrapedBulkData.objects.bulk_create(records_to_create)

        return {
            'status': 'success',
            'total_products': len(products),
            'records_created': records_created
        }
    
    except Exception as e:
        logger.error(f"Error in scrape_Bulk_product_task: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }

    

# # @shared_task
# def scrape_prices_task(sample_size=3):
#     try:
#         # Fetch the specific product by title
#         product_title = 'TestISA_only_one'
#         product = Product.objects.filter(TITLE=product_title).first()
        
#         if not product:
#             raise ValueError(f"No product found with title '{product_title}'")

#         # In this case, you're testing with a single product
#         products = [product]

#         dawa_urls = [link.url for product in products for link in product.account_links.filter(account__name='dawa')]
#         nahdi_urls = [link.url for product in products for link in product.account_links.filter(account__name='nahdi')]
#         amazon_urls = [link.url for product in products for link in product.account_links.filter(account__name='amazon')]

#         # Debug logging
#         logger.info(f"Dawa URLs2: {dawa_urls}")
#         logger.info(f"Nahdi URLs2: {nahdi_urls}")
#         logger.info(f"Amazon URLs2: {amazon_urls}")

#         # Scrape prices from each source
#         prices_dawa = scrape_prices_from_dawa(dawa_urls)
#         prices_nahdi = scrape_prices_from_nahdi(nahdi_urls)
#         prices_amazon, amazon_shipping, amazon_sold = scrape_prices_from_amazon(amazon_urls)

#         # Fill empty lists with zeros or defaults
#         max_length = max(len(prices_dawa), len(prices_nahdi), len(prices_amazon), len(amazon_shipping), len(amazon_sold))

#         prices_dawa.extend([None] * (max_length - len(prices_dawa)))
#         prices_nahdi.extend([None] * (max_length - len(prices_nahdi)))
#         prices_amazon.extend([None] * (max_length - len(prices_amazon)))
#         amazon_shipping.extend([None] * (max_length - len(amazon_shipping)))
#         amazon_sold.extend([None] * (max_length - len(amazon_sold)))

#         # Debug logging
#         logger.info(f"Prices Dawa: {prices_dawa}")
#         logger.info(f"Prices Nahdi: {prices_nahdi}")
#         logger.info(f"Prices Amazon: {prices_amazon}")
#         logger.info(f"Amazon Shipping: {amazon_shipping}")
#         logger.info(f"Amazon Sold By: {amazon_sold}")

#         # Create ScrapedData entries for the sample products
#         records_created = 0
#         for price_dawa, price_nahdi, price_amazon, ship_amazon, sold_amazon in zip(prices_dawa, prices_nahdi, prices_amazon, amazon_shipping, amazon_sold):
#             ScrapedData.objects.create(
#                 product=product,
#                 dawa_price=price_dawa,
#                 nahdi_price=price_nahdi,
#                 amazon_price=price_amazon,
#                 amazon_shipping=ship_amazon,
#                 amazon_sold_by=sold_amazon,
#             )
#             records_created += 1

#         # Return a summary of the task
#         return {
#             'status': 'success',
#             'total_products': len(products),
#             'records_created': records_created
#         }
    
#     except Exception as e:
#         # Return error details if an exception occurs
#         logger.error(f"Task failed with error: {e}")
#         return {
#             'status': 'failed',
#             'error': str(e)
#         }
