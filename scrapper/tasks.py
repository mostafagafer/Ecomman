from celery import shared_task
from .models import Product, ScrapedData
from .selenium_codes.Scrapper_functions import scrape_prices_from_dawa, scrape_prices_from_nahdi, scrape_prices_from_amazon
import random
import psutil
import time
import logging

logger = logging.getLogger(__name__)



@shared_task
def scrape_prices_task(sample_size=1):
    try:
        # Fetch all products
        all_products = Product.objects.all()
        
        # Select a random sample of products
        if all_products.count() > sample_size:
            products = random.sample(list(all_products), sample_size)
        else:
            products = all_products
        
        # Extract URLs from the sample products
        dawa_urls = [link.url for product in products for link in product.account_links.filter(account__name='dawa')]
        nahdi_urls = [link.url for product in products for link in product.account_links.filter(account__name='nahdi')]
        amazon_urls = [link.url for product in products for link in product.account_links.filter(account__name='amazon')]
        


        # Scrape prices from each source
        prices_dawa = scrape_prices_from_dawa(dawa_urls)
        prices_nahdi = scrape_prices_from_nahdi(nahdi_urls)
        prices_amazon, amazon_shipping, amazon_sold = scrape_prices_from_amazon(amazon_urls)


        # Fill empty lists with zeros or defaults
        max_length = max(len(prices_dawa), len(prices_nahdi), len(prices_amazon), len(amazon_shipping), len(amazon_sold))

        prices_dawa.extend([None] * (max_length - len(prices_dawa)))
        prices_nahdi.extend([None] * (max_length - len(prices_nahdi)))
        prices_amazon.extend([None] * (max_length - len(prices_amazon)))
        amazon_shipping.extend([None] * (max_length - len(amazon_shipping)))
        amazon_sold.extend([None] * (max_length - len(amazon_sold)))

        # Create ScrapedData entries for the sample products
        records_created = 0
        for product, price_dawa, price_nahdi, price_amazon, ship_amazon, sold_amazon in zip(products, prices_dawa, prices_nahdi, prices_amazon, amazon_shipping, amazon_sold):
            ScrapedData.objects.create(
                product=product,
                dawa_price=price_dawa,
                nahdi_price=price_nahdi,
                amazon_price=price_amazon,
                amazon_shipping=ship_amazon, 
                amazon_sold_by=sold_amazon     
            )
            records_created += 1

        # Debug logging
        logger.info(f"Prices Dawa: {prices_dawa}")
        logger.info(f"Prices Nahdi: {prices_nahdi}")
        logger.info(f"Prices Amazon: {prices_amazon}")
        logger.info(f"Amazon Shipping: {amazon_shipping}")
        logger.info(f"Amazon Sold By: {amazon_sold}")

        # Return a summary of the task
        return {
            'status': 'success',
            'total_products': len(products),
            'records_created': records_created
        }
    
    except Exception as e:
        # Return error details if an exception occurs
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
