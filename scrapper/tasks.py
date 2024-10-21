from celery import shared_task
from client_profile.models import Profile  # Ensure this import matches the app where Profile is located
from .models import Product, ScrapedData
from .selenium_codes.Scrapper_functions import scrape_prices_from_dawa, scrape_prices_from_nahdi, scrape_prices_from_amazon 
from .selenium_codes.Requests_functions import *
import random
import psutil
import time
import logging
import aiohttp
import asyncio

logger = logging.getLogger(__name__)



@shared_task
def scrape_prices_task(sample_size=50):
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
            # Fetch identifiers for the current product
            dawa_id = [link.identifier for link in product.account_id_links.filter(account_id__name='dawa')]
            nahdi_id = [link.identifier for link in product.account_id_links.filter(account_id__name='nahdi')]
            amazon_id = [link.identifier for link in product.account_id_links.filter(account_id__name='amazon')]
            
            # Fetch prices for each identifier
            # If no identifiers, use `None` to indicate no data
            amazon_prices, amazon_shipping, amazon_sold = (loop.run_until_complete(get_amazon_product_details(amazon_id))
                                                           if amazon_id else ([None], [None], [None]))
            price_dawa = loop.run_until_complete(get_dawa_prices(dawa_id)) if dawa_id else [None]
            price_nahdi = loop.run_until_complete(get_nahdi_prices(nahdi_id)) if nahdi_id else [None]

            # Extract the first element as we only expect a single value for each
            price_dawa = price_dawa[0] if price_dawa else None
            price_nahdi = price_nahdi[0] if price_nahdi else None
            price_amazon = amazon_prices[0] if amazon_prices else None
            ship_amazon = amazon_shipping[0] if amazon_shipping else None
            sold_amazon = amazon_sold[0] if amazon_sold else None

            # Log scraped data for debugging
            logger.info(f"Prices Dawa: {price_dawa}")
            logger.info(f"Prices Nahdi: {price_nahdi}")
            logger.info(f"Prices Amazon: {price_amazon}")
            logger.info(f"Amazon Shipping: {ship_amazon}")
            logger.info(f"Amazon Sold By: {sold_amazon}")

            # Create a record for the current product
            records_to_create.append(ScrapedData(
                product=product,
                dawa_price=price_dawa,
                nahdi_price=price_nahdi,
                amazon_price=price_amazon,
                amazon_shipping=ship_amazon,
                amazon_sold_by=sold_amazon
            ))
            records_created += 1

        # Bulk create ScrapedData entries for efficiency
        ScrapedData.objects.bulk_create(records_to_create)
        
        # Return a summary of the task
        return {
            'status': 'success',
            'total_products': len(products),
            'records_created': records_created
        }
    
    except Exception as e:
        # Log the error and return error details if an exception occurs
        logger.error(f"Error in scrape_prices_task: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }



@shared_task
def scrape_user_products_task(product_ids):
    try:
        # Fetch the products based on the passed IDs
        products = Product.objects.filter(id__in=product_ids)
        
        records_to_create = []
        records_created = 0
        loop = asyncio.get_event_loop()

        for product in products:
            # Fetch identifiers for the current product
            dawa_id = [link.identifier for link in product.account_id_links.filter(account_id__name='dawa')]
            nahdi_id = [link.identifier for link in product.account_id_links.filter(account_id__name='nahdi')]
            amazon_id = [link.identifier for link in product.account_id_links.filter(account_id__name='amazon')]

            # Fetch prices for each identifier with delay
            amazon_prices, amazon_shipping, amazon_sold = (loop.run_until_complete(get_amazon_product_details(amazon_id))
                                                    if amazon_id else ([None], [None], [None]))
            # time.sleep(2)  # Add a delay of 2 seconds between requests
            # print('weight 2 sec')
            price_dawa = loop.run_until_complete(get_dawa_prices(dawa_id)) if dawa_id else [None]
            # time.sleep(2)  # Add a delay of 2 seconds between requests
            # print('weight 2 sec')  # Add a delay of 2 seconds between requests
            price_nahdi = loop.run_until_complete(get_nahdi_prices(nahdi_id)) if nahdi_id else [None]
            # time.sleep(2)  # Add a delay of 2 seconds between requests
            # print('weight 2 sec')            

            # Extract the first element as we only expect a single value for each
            price_dawa = price_dawa[0] if price_dawa else None
            price_nahdi = price_nahdi[0] if price_nahdi else None
            price_amazon = amazon_prices[0] if amazon_prices else None
            ship_amazon = amazon_shipping[0] if amazon_shipping else None
            sold_amazon = amazon_sold[0] if amazon_sold else None

            # Create a record for the current product
            records_to_create.append(ScrapedData(
                product=product,
                dawa_price=price_dawa,
                nahdi_price=price_nahdi,
                amazon_price=price_amazon,
                amazon_shipping=ship_amazon,
                amazon_sold_by=sold_amazon
            ))
            records_created += 1

        # Bulk create ScrapedData entries for efficiency
        ScrapedData.objects.bulk_create(records_to_create)
        
        # Return a summary of the task
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
