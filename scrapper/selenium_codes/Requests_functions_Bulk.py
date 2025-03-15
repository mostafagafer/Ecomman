from bs4 import BeautifulSoup
import aiohttp
import asyncio
import pandas as pd
import re
import json
import logging
from scrapper.utils import parse_discount_from_text


# old code changed in 22/12/2024
# async def fetch_amazon_search_results(session, query, num_products):
#     query_updated = query.replace(" ", "+")
#     page = 1
#     products = []    
    
#     base_url = 'https://www.amazon.sa/s'

#     headers = {
#         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#         'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
#         'cookie': 'session-id=258-6012606-2561645; i18n-prefs=SAR; ubid-acbsa=257-1535786-5196730; lc-acbsa=en_AE; session-id-time=2082787201l; session-token=OpmNbjJzw5oWMMDfwOq6ulXjKxrI3t64CVz9/dipmaCv83rv32RxTrxJ9uKE6BXdOAA0frbGXAXS8mX4z+3YzarfFdo8MD7rHf++Jg229SzcD4XHiXdZge5veFvjgVR3xZwqxj/6x8wkGjppRbVcBlKrxkAiLN6lM485DXbMrga9Dlv9HV7Dq4y0DGXIi7WwTTvo200JvtMHFJ3h2zrRQNBWDAvitxJUu97phcXCfT/1q/dTN1Jwr0YsLKNDTVQhGIWkKMQrmQRow0OrbbcO/5tY6B46TzJViNN3ZURoCga8avivzCKTD6sTp8cURx8BwpYutiLMW4FiTqyEJZlVuGxdBw2AH7T7; csm-hit=tb:HKRBZ9MFZ0V9WEVSDK14+s-4K6Y2K7CBW55KR10YN9S|1727798078925&t:1727798078925&adb:adblk_yes',
#         'device-memory': '8',
#         'downlink': '10',
#         'dpr': '0.6666666666666666',
#         'ect': '4g',
#         'priority': 'u=0, i',
#         'rtt': '150',
#         'sec-ch-device-memory': '8',
#         'sec-ch-dpr': '0.6666666666666666',
#         'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Windows"',
#         'sec-ch-ua-platform-version': '"10.0.0"',
#         'sec-ch-viewport-width': '1007',
#         'sec-fetch-dest': 'document',
#         'sec-fetch-mode': 'navigate',
#         'sec-fetch-site': 'none',
#         'sec-fetch-user': '?1',
#         'upgrade-insecure-requests': '1',
#         'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
#         'viewport-width': '1007',
#     }

#     while len(products) < num_products:
#         params = {
#             'k': query_updated,
#             'page': page,
#             'language': 'en'
#         }
        
#         async with session.get(base_url, headers=headers, params=params) as response:
#             content = await response.text()
#             soup = BeautifulSoup(content, 'html.parser')
            

            
#             # Find all product containers on the page
#             product_elements = soup.select('.s-main-slot .s-result-item')
#             products = []

#             for product in product_elements:
#                 # Try to get ASIN from data-asin, or retrieve it by inspecting attributes
#                 asin = product.get('data-asin', None)
#                 if not asin:
#                     asin_tag = product.get('data-asin')
#                     asin = asin_tag if asin_tag else None

#                 # Check for the title element and extract it if present
#                 title_element = product.select_one('h2 .a-text-normal')
#                 if title_element:
#                     title = title_element.get_text(strip=True)
#                     print(f"Product Title: {title}")  # Print each title to the terminal

#                     # Get the current price, convert to float
#                     current_price_element = product.select_one('.a-row.a-size-base.a-color-base .a-price .a-offscreen')
#                     current_price_text = current_price_element.get_text(strip=True) if current_price_element else None
#                     current_price = float(re.sub(r'[^\d.]', '', current_price_text)) if current_price_text else None

#                     # Get the original price (before discount), convert to float
#                     original_price_element = product.select_one('.a-row.a-size-base.a-color-base .a-price.a-text-price .a-offscreen')
#                     original_price_text = original_price_element.get_text(strip=True) if original_price_element else None
#                     original_price = float(re.sub(r'[^\d.]', '', original_price_text)) if original_price_text else None

#                     # Calculate the discount percentage if original price is available
#                     amazon_discount = (100-(current_price / original_price * 100)) if current_price and original_price else None

#                     # Extract purchase count text if available
#                     purchase_count_element = product.select_one('span.a-size-base.a-color-secondary')
#                     purchase_count_text = purchase_count_element.get_text(strip=True) if purchase_count_element else None

#                     # Print ASIN, prices, discount, and purchase count to the terminal
#                     print(f"ASIN: {asin}, Current Price: {current_price}, Original Price: {original_price}, "
#                         f"Discount: {amazon_discount}, Purchase Count: {purchase_count_text}")

#                     # Append the product data to the list
#                     products.append({
#                         'ASIN': asin,
#                         'title': title,
#                         'current_price': current_price,
#                         'original_price': original_price,
#                         'amazon_discount': amazon_discount,
#                         'purchase_count': purchase_count_text
#                     })

                
#                 # Stop if we've collected the desired number of products
#                 if len(products) >= num_products:
#                     break
            
#             page += 1

#             # If no products found on the page, break to avoid infinite loop
#             if not product_elements:
#                 print("No more products found.")
#                 break

#     return products

# async def get_amazon_details(amazon_queries, num_products):
#     async with aiohttp.ClientSession() as session:
#         # Create asynchronous tasks for each Amazon query
#         tasks = [fetch_amazon_search_results(session, query, num_products) for query in amazon_queries]
        
#         # Gather responses for each query
#         responses = await asyncio.gather(*tasks)
        
#         # Process and structure Amazon data
#         all_amazon_data = []
#         for response, query in zip(responses, amazon_queries):
#             if response:  # Check if response contains data
#                 for product in response:
#                     all_amazon_data.append({
#                         'ASIN': product.get('ASIN'),
#                         'title': product.get('title'),
#                         'current_price': product.get('current_price'),
#                         'original_price': product.get('original_price'),
#                         'amazon_discount': product.get('amazon_discount'),
#                         'purchase_count': product.get('purchase_count'),
#                         'key': query  # Store the query as 'key'
#                     })
        
#         return all_amazon_data


# new  code
async def fetch_amazon_search_results(session, query, num_products):
    query_updated = query.replace(" ", "+")
    page = 1
    products = []    
    
    base_url = 'https://www.amazon.sa/s'

    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
    'cache-control': 'no-cache',
    'cookie': 'session-id=258-6012606-2561645; i18n-prefs=SAR; ubid-acbsa=257-1535786-5196730; lc-acbsa=en_AE; session-token=2O6CMqMgveZzEjnpvpbrVcdVjFM+yHCNqpvtVTZFyG4o6WbdbXmKYuifwwfIzVoioeTy1qkSBxE1nHxuPIdMOaNfiN1coOMJyHy//6iD19TTZ8cenuwRLDRV5LAjUWeKyA0QTYZ2XNPEG2wjSZncCAyixDUxV0+e3h5SN5X+xp1MeVo1rKmCJb6sQMNgnGQgsDAoIdFqqROQocvosyjRlRpacq6ch51bzTMrZxPijmH24TK8tTLyq3xPO4H36MpVmjUkyvg4r1XVmPoEbscWggKzsUmRO2+fqmLQt/oL6DYm0rqmnVjB/HA8EnMUizldT4VHRLTyJMF6Rc3lmu6eXKor+AEsBleY; csm-hit=tb:s-FZQQRKF9CCAJVDA7XEEJ|1734598252871&t:1734598254997&adb:adblk_yes; session-id-time=2082758401l',
    'device-memory': '8',
    'downlink': '10',
    'dpr': '0.6666666666666666',
    'ect': '4g',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://www.amazon.sa/',
    'rtt': '100',
    'sec-ch-device-memory': '8',
    'sec-ch-dpr': '0.6666666666666666',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-ch-viewport-width': '1149',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'viewport-width': '1149',
    }

    while len(products) < num_products:
        params = {
            'k': query_updated,
            'page': page,
            'language': 'en'
        }
        print(f"Fetching Amazon data for query '{query}' with num_products={num_products}")

        async with session.get(base_url, headers=headers, params=params) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            listitems = soup.find_all('div', role='listitem')

            # print(f"Found {len(listitems)} listitems on page {page}")
            if not listitems:
                print(f"No more products found on page {page}.")
                break
            
            for product in listitems:
                
                # Extract title
                title_element = product.select_one('h2.a-text-normal')
                title = title_element.get_text(strip=True) if title_element else None


                # Extract ASIN
                asin = product.get('data-asin', None)

                # Extract current price
                current_price_element = product.select_one('.a-row.a-size-base.a-color-base .a-price .a-offscreen')
                current_price_text = current_price_element.get_text(strip=True) if current_price_element else None
                current_price = (
                    float(re.sub(r'[^\d.]', '', current_price_text))
                    if current_price_text else None
                )

                # Extract original price
                original_price_element = product.select_one('div.a-section.aok-inline-block .a-price.a-text-price .a-offscreen')
                original_price_text = original_price_element.get_text(strip=True) if original_price_element else None
                original_price = (
                    float(re.sub(r'[^\d.]', '', original_price_text))
                    if original_price_text else None
                )

                # Calculate discount percentage
                amazon_discount = (
                    100 - (current_price / original_price * 100)
                    if current_price and original_price else None
                )

                # Extract purchase count
                purchase_count_element = product.select_one('span.a-size-base.a-color-secondary')
                purchase_count_text = purchase_count_element.get_text(strip=True) if purchase_count_element else None

                # Append data
                products.append({
                    'title': title,
                    'asin': asin,
                    'current_price': current_price,
                    'original_price': original_price,
                    'amazon_discount': amazon_discount,
                    'purchase_count': purchase_count_text,
                })

                # Stop if we've collected enough products
                if len(products) >= num_products:
                    break

        page += 1
        await asyncio.sleep(2)  # Add delay to prevent throttling

    return products

async def get_amazon_details(amazon_queries, num_products):
    async with aiohttp.ClientSession() as session:
        # Create asynchronous tasks for each Amazon query
        tasks = [fetch_amazon_search_results(session, query, num_products) for query in amazon_queries]
        
        # Gather responses for each query
        responses = await asyncio.gather(*tasks)
        
        # Process and structure Amazon data
        all_amazon_data = []
        for response, query in zip(responses, amazon_queries):
            if response:  # Check if response contains data
                for product in response:
                    all_amazon_data.append({
                        'ASIN': product.get('asin'),
                        'title': product.get('title'),
                        'current_price': product.get('current_price'),
                        'original_price': product.get('original_price'),
                        'amazon_discount': product.get('amazon_discount'),
                        'purchase_count': product.get('purchase_count'),
                        'key': query  # Store the query as 'key'
                    })
        
        return all_amazon_data


async def fetch_dawa_data(session, query, num_products):
    query_updated = query.replace(" ", "%20")
    url = 'https://l1p3f2vbnf-3.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.13.1)%3B%20Browser%3B%20instantsearch.js%20(4.41.0)%3B%20Magento2%20integration%20(3.10.5)%3B%20JS%20Helper%20(3.8.2)'
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://www.al-dawaa.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.al-dawaa.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-algolia-api-key': 'MWQzMjEzYTYyOGNhM2M4MzkwM2E1M2U3MTZmOTM3MGY1ZDIyYjhiMTk1NGU5NDk0MmI2ZDZjZjdmOTAyODU2M3RhZ0ZpbHRlcnM9',
        'x-algolia-application-id': 'L1P3F2VBNF',
    }

    payload = {
        "requests": [{
            "indexName": "magento2_productionenglish_products",
            "params": (
                f"highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&page=0"
                f"&ruleContexts=%5B%22magento_filters%22%5D&hitsPerPage={num_products}&clickAnalytics=true"
                f"&query={query_updated}&maxValuesPerFacet=10"
                f"&facets=%5B%22brand%22%2C%22diaper_size%22%2C%22features%22%2C%22product_function%22"
                f"%2C%22duration%22%2C%22gender%22%2C%22package%22%2C%22product_form%22%2C%22area_covered%22"
                f"%2C%22color%22%2C%22skin_concern%22%2C%22age%22%2C%22volume%22%2C%22ingredients%22%2C%22scent%22"
                f"%2C%22hair_type%22%2C%22skin_type%22%2C%22diaper_number%22%2C%22milk_number%22%2C%22price.SAR.default%22"
                f"%2C%22categories.level0%22%5D&tagFilters=&numericFilters=%5B%22visibility_search%3D1%22%5D"
            )
        }]
    }

    print(f"Fetching Dawa data for query '{query}' with num_products={num_products}")

    async with session.post(url, json=payload, headers=headers) as response:
        try:
            response_data = await response.json()
            hits = response_data.get("results", [])[0].get("hits", [])
            # print(f"Query '{query}' returned {len(hits)} products in Dawa.")
        except aiohttp.ContentTypeError:
            print(f"Failed to fetch data for Dawa for query '{query}'.")
            response_data = {"results": []}
        return response_data, query

def process_dawa_response(data, query):
    dawa_data = []
    for result in data.get('results', []):
        hits = result.get('hits', [])
        for hit in hits:
            original_price = hit.get('price', {}).get('SAR', {}).get('default_original_formated', None)
            if original_price:
                original_price = float(original_price.replace(' SAR', '').replace(',', '').strip())

            # Extract offer text
            offer_text_notag = hit.get('offer_text_notag', None)
            
            # Calculate discount
            discount = parse_discount_from_text(offer_text_notag) if offer_text_notag else 0

            dawa_data.append({
                'name': hit.get('name', None),
                'price': hit.get('price', {}).get('SAR', {}).get('default', None),
                'price_original': original_price,
                'offer_text_notag': hit.get('offer_text_notag', None),
                'sku': hit.get('sku', None),
                'discount': discount,
                'key': query  # Include the query as the key
            })
    return pd.DataFrame(dawa_data)

async def get_dawa_details(dawa_queries, num_products):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_dawa_data(session, query, num_products) for query in dawa_queries]
        responses = await asyncio.gather(*tasks)
        all_dawa_data = [process_dawa_response(response, query) for (response, query) in responses]

        result = []
        for data in all_dawa_data:
            for entry in data.itertuples(index=False):
                result.append({
                    'name': entry.name,
                    'price': entry.price,
                    'price_original': entry.price_original,
                    'offer_text_notag': entry.offer_text_notag,
                    'sku': entry.sku,
                    'key': entry.key,  # Add 'key' in the final result
                    'discount': entry.discount,
                })

        return result


async def fetch_nahdi_data(session, query, num_products):
    query_updated = query.replace(" ", "%20")
    url = 'https://h9x4ih7m99-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.14.3)%3B%20Browser%3B%20instantsearch.js%20(4.63.0)%3B%20Magento2%20integration%20(3.13.3)%3B%20JS%20Helper%20(3.16.1)'
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://www.nahdionline.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.nahdionline.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-algolia-api-key': 'YTVlMDc5OGNmZGM4YzhiNTBhNzg0MTc3ZDBlYWU1NjQ3NzQzNTE5YTFhOGM4OTc5MGM1MzE3MjBlZDk0YzhmMnRhZ0ZpbHRlcnM9',
        'x-algolia-application-id': 'H9X4IH7M99',
    }
    
    payload = {
        "requests": [{
            "indexName": "prod_en_products",
            "params": (
                f"analyticsTags=%5B%22Desktop%22%2C%22search-page%22%5D"
                f"&clickAnalytics=true&facets=%5B%22age_range%22%2C%22categories.level0%22%2C"
                f"%22color%22%2C%22concentration%22%2C%22consumption_size%22%2C%22country_of_origin%22%2C"
                f"%22finish%22%2C%22flavor%22%2C%22free_from%22%2C%22gender%22%2C%22global_filter%22%2C"
                f"%22hair_type%22%2C%22hidden_item%22%2C%22imf_category%22%2C%22imf_class%22%2C"
                f"%22imf_department%22%2C%22imf_division%22%2C%22imf_matrix_segment_1%22%2C"
                f"%22imf_matrix_segment_2%22%2C%22imf_segment5%22%2C%22imf_sub_category%22%2C"
                f"%22imf_sub_class%22%2C%22ingredient%22%2C%22item_has_offer%22%2C%22landing_categories%22%2C"
                f"%22lens_type%22%2C%22lense_power%22%2C%22manufacturer%22%2C%22pack_size_volume%22%2C"
                f"%22price.SAR.default%22%2C%22product_form%22%2C%22product_function%22%2C"
                f"%22product_type_string%22%2C%22quantity%22%2C%22scent%22%2C%22serving_size%22%2C"
                f"%22shade%22%2C%22size%22%2C%22skin_type%22%2C%22sku%22%2C%22special_features%22%5D"
                f"&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__"
                f"&hitsPerPage={num_products}&maxValuesPerFacet=100&numericFilters=%5B%22visibility_search%3D1%22%5D"
                f"&page=0&query={query_updated}&ruleContexts=%5B%22magento_filters%22%5D&tagFilters="
            )
        }]
    }
    print(f"Fetching Nahdi data for query '{query}' with num_products={num_products}")
  
    async with session.post(url, json=payload, headers=headers) as response:
        try:
            response_data = await response.json()
            hits = response_data.get("results", [])[0].get("hits", [])
            # print(f"Query '{query}' returned {len(hits)} products.")
            # print(f"Query '{query}' returned {len(hits)} products in Nahdi.")
        except aiohttp.ContentTypeError:
            print(f"Failed to fetch data for Nahdi for query '{query}'.")
            response_data = {"results": []}
        return response_data, query

def process_nahdi_response(data, query):
    nahdi_data = []
    for result in data.get('results', []):
        hits = result.get('hits', [])
        for hit in hits:  # Loop through all hits
            # Extract the necessary fields with default values if not found
            original_price = hit.get('price', {}).get('SAR', {}).get('default_original_formated', None)
            price = hit.get('price', {}).get('SAR', {}).get('default', None)

            # Remove " SAR" and commas, then convert to float if not None
            if original_price:
                original_price = float(original_price.replace(' SAR', '').replace(',', '').strip())
             # Apply the coalesce logic to determine the effective price
            if original_price is None:
                discount = 0
            else:
                discount = (100 - (price/original_price)* 100  )                
            nahdi_data.append({
                'name': hit.get('name', None),
                'price': hit.get('price', {}).get('SAR', {}).get('default', None),
                'price_original': original_price,
                'ordered_qty': hit.get('ordered_qty', None),
                'sku': hit.get('sku', None),
                'key': query,  # Include the query as the key
                'discount': discount,
            })
    return pd.DataFrame(nahdi_data)  # Return DataFrame directly

async def get_nahdi_details(nahdi_queries, num_products):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_nahdi_data(session, query, num_products) for query in nahdi_queries]
        responses = await asyncio.gather(*tasks)
        all_nahdi_data = [process_nahdi_response(response, query) for (response, query) in responses]

        # Flatten the results into a list of dictionaries
        result = []
        for data in all_nahdi_data:
            for entry in data.itertuples(index=False):
                result.append({
                    'name': entry.name,
                    'price': entry.price,
                    'price_original': entry.price_original,
                    'ordered_qty': entry.ordered_qty,
                    'sku': entry.sku,
                    'key': entry.key,  # Add 'key' in the final result
                    'discount': entry.discount,
            })

        return result



# Function to fetch data from Noon.sa
async def fetch_noon_data(session, query, num_products):
    # Replace spaces in the query with URL encoding
    query_updated = query.replace(" ", "%20")
    
    # Construct the URL with query parameters
    url = (
        f"https://www.noon.com/saudi-en/search/"
        f"?q={query_updated}&isCarouselView=false&limit={num_products}&sort%5Bby%5D=popularity&sort%5Bdir%5D=desc"
    )
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'visitor_id=bc156d3c-96ce-4a6b-a3a5-4aa64c31c134; _gcl_au=1.1.131444729.1727515428; _ga=GA1.2.1083881771.1727515444; _scid=reVr5GO4avCloaxPAnOKA7j6J26n53U4; _tt_enable_cookie=1; nloc=en-sa; _ScCbts=%5B%22260%3Bchrome.2%3A2%3A5%22%5D; _sctr=1%7C1731794400000; _ttp=_MLtL_L6O-TWV85lmATLBMEw8sJ.tt.1; review_lang=xx; th_capi_ph=66d791a4b43e9b0607f115746aa8b70d93b5eda23775d84ef19b2bc80f7caa53; ZLD887450000000002180avuid=7a9c821e-7e27-451a-ae45-114ebfff68bd; _clck=8x43rh%7C2%7Cfr2%7C0%7C1732; AKA_A2=A; bm_mi=FCA04E41935E3118143BBD4A9C723F06~YAAQpTwSAhNoqSaTAQAATL3YTRnQ5U+/iVa781N+o2E6hiAhZW8tKeswbhn3+6MK4FZ+KATU1nbDAIYjagq3v8WtZA8PSCBmZyFxfe5HpZNzi83lZM5NoEgsZrfxcXekK0WfWZ2IrvHJ1bW/AFOARpH5rvydBZXAXZqELPcMclQutQjtafvOuN/lTmkiif71eOUx3Vs385U9UHJBzrjfpACqW/y0eXC6gKnJBN2uOVOyrYVMGJDi0cnbErR0pd/C4uoFF47753gn/qxRMT6Z17XViG9+hiRML/CWR8JNrMj2gbYmp10/fN3vDyJZ8SC6m4TSr2WUyF/p~1; _etc=sQkaOpSXI805sGeo; ak_bmsc=6E1F9453FD6AC43CA734CB867C8ABB2D~000000000000000000000000000000~YAAQpTwSAt5rqSaTAQAATADZTRnRJpqROkEESfsqSzVmOi4bF84ftNkPsw4yH/lkpE5e6nkxKEMZlp7/AloofbrduXJnbarnAOVM1zVcQGK5owrXJQvv13DuQMA+rIll1E+TbrKRn2DpGFtVXIa11m6R+u3K/m6lStVVF678PfbZ6X9qLGUT+0CY8VX3gv+AMt4tfgm6t5TzDu+f8094z3v4Kvx6rDxwHIYBHglB7N9uH6K0dw9CZj+2JSPINapl30quMYsuIV6Y0eevwFjyNF57yQkHT/97lmXoKPIYtfD0WsePwlySAnHuQJZBcEl7dasHKokvfF0xgOhRgm6qAoiGXz4lRA1Swd5UdR86BLHeRtEXUOVam1rXJtQjVYjhRxaJvF9c4/SlUArTMNEhA9Vlr2K5zSISoLQCMSh+lnVsPlaKsKsbkHbsFkVPCZf55hOGWq8AJDuckP+u9cPpkoHX7Y/RlNKz4KN6gvE=; ZLDsiq3b3ce696144e42ab351af48092266ce3dda2b3c7b2ad6e09ba5d18504de03180tabowner=undefined; x-whoami-headers=eyJ4LWxhdCI6IjI0NzMxMTM4MiIsIngtbG5nIjoiNDY2NzAwODE0IiwieC1hYnkiOiJ7XCJwb192MlwiOntcImVuYWJsZWRcIjoxfSxcInNwbF92MlwiOntcImVuYWJsZWRcIjoxfSxcInNwbF92M1wiOntcImVuYWJsZWRcIjoxfSxcInBkcF9ib3NcIjp7XCJlbmFibGVkXCI6MX0sXCJtcF9pY29uX3YyXCI6e1wiZW5hYmxlZFwiOjF9LFwiZ2xvYmFsX2V4cFwiOntcImVuYWJsZWRcIjoxfSxcInBkcF9mbHlvdXRcIjp7XCJmbHlvdXRfdmFsdWVcIjowfSxcInNwbF9lbnRyeXBvaW50X3YyXCI6e1wiZW5hYmxlZFwiOjF9LFwid2ViX3BscF9wZHBfcmV2YW1wXCI6e1wiZW5hYmxlZFwiOjF9LFwicGRwX3NjcmVlbnNob3Rfc2hhcmVfc2hlZXRcIjp7XCJlbmFibGVkXCI6MX19IiwieC1lY29tLXpvbmVjb2RlIjoiU0EtUlVILVMxNyIsIngtYWItdGVzdCI6WzcxMSw3MjEsODMwLDg1MSw5MDEsOTExLDkyMSw5NDEsOTUxLDk4MSwxMDIxLDEwMzEsMTA3MCwxMDkxLDExMDFdLCJ4LXJvY2tldC16b25lY29kZSI6IlcwMDA4MzQ5NkEiLCJ4LXJvY2tldC1lbmFibGVkIjp0cnVlLCJ4LWJvcmRlci1lbmFibGVkIjp0cnVlfQ==; noonengr-_zldp=dbw5UOFoeCxTgBnt0REV5btd8c%252F9rlL%252F68HewXjBFT2AMAvt7hW%252BtnXnGuTlF%252FYYmKwM1K1ctjo%253D; ZLDsiq663f5c2580454f7ed6b7bbe12e575c5570eb9b21832ce32b902ca6cbca6ffc2bavuid=7a9c821e-7e27-451a-ae45-114ebfff68bd; nguestv2=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJraWQiOiI0MDU2OTczNjU2NDk0ZTRmODBjNWE2Y2FlNDZlZDI5OCIsImlhdCI6MTczMjE3OTMxNywiZXhwIjoxNzMyMTc5NjE3fQ.xOUtDJnjH0_Wigy_uVpQiGLFDea2BsvvvU7V3UUkrqc; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22j0CBwPXiOd9ZcoSgCypn%22%2C%22expiryDate%22%3A%222025-11-21T08%3A55%3A20.199Z%22%7D; _scid_r=sWVr5GO4avCloaxPAnOKA7j6J26n53U4zWuXiQ; _uetsid=19c63c70a71711ef9aef1116598f49c2; _uetvid=692459107d7b11ef8c8f67cbdc118fe8; bm_sv=EDB046D9F1AAFDCD4FBB281D8017F132~YAAQpTwSAj+sqiaTAQAA7/jvTRk1u5S1rCTXUQnwXU+8xERnnwI2BuxAQX/3oyMYF3l9+auo8bnilJ05fsd4MXzs8oG6EJDnyiSgD7kAQKahdhIbokXJZnKrO9QgG8CyBQYaTFnep0vJyp9CDqkCYt4sCjTav2HCAlq167vZAeUSlxcNrZlXJ3oQkkie0OaUdyO2PFslngELBUdDIuHEru/10cMqxDHvyCz/uM6lvl0T6rb0hF9tIf5Y2lLCUm4=~1; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3Anull%2C%22expiryDate%22%3A%222025-11-21T08%3A56%3A38.498Z%22%7D; _clsk=apwh48%7C1732179400015%7C8%7C0%7Ck.clarity.ms%2Fcollect; RT="z=1&dm=noon.com&si=7c7fb5a4-0b13-4006-9a69-a7e33ff6dd20&ss=m3r1z8c4&sl=1&tt=w2p&rl=1&nu=d41d8cd98f00b204e9800998ecf8427e&cl=wnbi&ul=x4wu"',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        }

    print(f"Fetching Noon data for query '{query}' with num_products={num_products}")
    try:
        async with session.get(url, headers=headers) as response:
            # print(f"Response status for '{query}': {response.status}")
            response_data = await response.text()
            return response_data, query
    except Exception as e:
        print(f"Error fetching data for query '{query}': {e}")
        return None


# Function to process the Noon response
# Function to process the Noon response
def process_noon_response(data, query):
    if not data:
        print(f"No data received for query '{query}'.")
        return pd.DataFrame()

    soup = BeautifulSoup(data, 'html.parser')
    
    # Extract product details
    products = soup.find_all('div', class_='ProductBoxVertical_wrapper__xPj_f')
    noon_data = []

    for product in products:
        # Extract product name
        product_name_tag = product.find('h2', class_='ProductDetailsSection_title__JorAV', attrs={'data-qa': 'product-name'})
        product_name = product_name_tag['title'] if product_name_tag else None
        
        # Extract current price
        current_price_tag = product.find('strong', class_='Price_amount__2sXa7')
        current_price = current_price_tag.text if current_price_tag else None
        current_price = float(current_price_tag.text.replace(',', '')) if current_price_tag else None
 
        # Extract original price
        original_price_tag = product.find('span', class_='Price_oldPrice__ZqD8B')
        original_price = original_price_tag.text if original_price_tag else None
        original_price = float(original_price_tag.text.replace(',', '')) if original_price_tag else None

        # Extract discount percentage
        discount_tag = product.find('span', class_='PriceDiscount_discount__1ViHb')
        discount = discount_tag.text if discount_tag else None
        if discount:
            discount = re.sub(r'[^0-9]', '', discount)
        
        # Extract SKU
        sku_tag = product.find('a', class_='ProductBoxLinkHandler_productBoxLink__FPhjp')
        sku = sku_tag['href'].split('/')[-2] if sku_tag else None
        
        # Check if the product is buyable
        
        noon_data.append({
            'product_name': product_name,
            'current_price': current_price,
            'original_price': original_price,
            'discount': discount,
            'sku': sku,
            'key': query  # Include the query as the key
        })

    return pd.DataFrame(noon_data)  # Return DataFrame directly

# Asynchronous task to fetch and return Noon data for multiple queries
async def get_noon_details(noon_queries, num_products):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_noon_data(session, query, num_products) for query in noon_queries]
        responses = await asyncio.gather(*tasks)
        all_noon_data = [process_noon_response(response, query) for (response, query) in responses]

        result = []
        for data in all_noon_data:
            for entry in data.itertuples(index=False):
                result.append({
                    'name': entry.product_name,
                    'price': entry.current_price,
                    'price_original': entry.original_price,
                    'discount': entry.discount,
                    'sku': entry.sku,
                    'key': entry.key  # Add 'key' in the final result
                })

        return result


# # Function to process the Noon response
# def process_noon_response(data, query):
#     # print("Processing HTML content...")
#     soup = BeautifulSoup(data, 'html.parser')
#     script_tag = soup.find('script', id="__NEXT_DATA__", type="application/json")
    
#     if not script_tag:
#         print("Error: __NEXT_DATA__ script not found in the HTML.")
#         return []

#     try:
#         data = json.loads(script_tag.string)
#         # print("Successfully parsed JSON data.")
#     except json.JSONDecodeError:
#         print("Error: Failed to parse JSON data.")
#         return []

#     # # Print the entire JSON structure for debugging
#     # with open("debug_noon_data.json", "w", encoding="utf-8") as f:
#     #     json.dump(data, f, indent=4)
#     # print("JSON structure saved to 'debug_noon_data.json' for inspection.")

#     # Extract hits and facets
#     noon_data = []
#     hits = data.get('props', {}).get('pageProps', {}).get('catalog', {}).get('hits', [])

#     # print(f"Number of hits: {len(hits)}")

#     for hit in hits:
#         name = hit.get('name')
#         price = hit.get('price')
#         original_price = hit.get('sale_price')

#         # Apply the coalesce logic to determine the effective price
#         if original_price is None:
#             effective_price = price
#             discount = 0
#         else:
#             effective_price = original_price
#             discount = (100 - (original_price/price)* 100  ) 



#         noon_data.append({
#             'name': name,
#             'price': price,
#             'sku': hit.get('sku', None),
#             'original_price': original_price,
#             'calculated_price': round(effective_price, 2),  # Final effective price
#             'discount': round(discount, 2),  # Discount percentage
#             'key': query  # Include the query as the key

#         })

#     # print(f"Processed {len(processed_data)} items.")
#     return pd.DataFrame(noon_data)  # Return DataFrame directly

# # Asynchronous task to fetch and return Noon data for multiple queries
# async def get_noon_details(noon_queries , num_products):
#     async with aiohttp.ClientSession() as session:
#         tasks = [fetch_noon_data(session, query, num_products) for query in noon_queries]
#         responses = await asyncio.gather(*tasks)
#         all_noon_data = [process_noon_response(response, query) for (response, query) in responses]

#         result = []
#         for data in all_noon_data:
#             for entry in data.itertuples(index=False):
#                 result.append({
#                     'name': entry.name,
#                     'price': entry.calculated_price,
#                     'price_original': entry.original_price,
#                     'discount': entry.discount,
#                     'sku': entry.sku,
#                     'key': entry.key  # Add 'key' in the final result
#                 })

#         return result



