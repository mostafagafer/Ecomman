from bs4 import BeautifulSoup
import aiohttp
import asyncio
import pandas as pd
import re
import json
import logging


async def fetch_amazon_search_results(session, query, num_products):
    query_updated = query.replace(" ", "+")
    page = 1
    products = []    
    
    base_url = 'https://www.amazon.sa/s'

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'cookie': 'session-id=258-6012606-2561645; i18n-prefs=SAR; ubid-acbsa=257-1535786-5196730; lc-acbsa=en_AE; session-id-time=2082787201l; session-token=OpmNbjJzw5oWMMDfwOq6ulXjKxrI3t64CVz9/dipmaCv83rv32RxTrxJ9uKE6BXdOAA0frbGXAXS8mX4z+3YzarfFdo8MD7rHf++Jg229SzcD4XHiXdZge5veFvjgVR3xZwqxj/6x8wkGjppRbVcBlKrxkAiLN6lM485DXbMrga9Dlv9HV7Dq4y0DGXIi7WwTTvo200JvtMHFJ3h2zrRQNBWDAvitxJUu97phcXCfT/1q/dTN1Jwr0YsLKNDTVQhGIWkKMQrmQRow0OrbbcO/5tY6B46TzJViNN3ZURoCga8avivzCKTD6sTp8cURx8BwpYutiLMW4FiTqyEJZlVuGxdBw2AH7T7; csm-hit=tb:HKRBZ9MFZ0V9WEVSDK14+s-4K6Y2K7CBW55KR10YN9S|1727798078925&t:1727798078925&adb:adblk_yes',
        'device-memory': '8',
        'downlink': '10',
        'dpr': '0.6666666666666666',
        'ect': '4g',
        'priority': 'u=0, i',
        'rtt': '150',
        'sec-ch-device-memory': '8',
        'sec-ch-dpr': '0.6666666666666666',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"10.0.0"',
        'sec-ch-viewport-width': '1007',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'viewport-width': '1007',
    }

    while len(products) < num_products:
        params = {
            'k': query_updated,
            'page': page,
            'language': 'en'
        }
        
        async with session.get(base_url, headers=headers, params=params) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            

            
            # Find all product containers on the page
            product_elements = soup.select('.s-main-slot .s-result-item')
            products = []

            for product in product_elements:
                # Try to get ASIN from data-asin, or retrieve it by inspecting attributes
                asin = product.get('data-asin', None)
                if not asin:
                    asin_tag = product.get('data-asin')
                    asin = asin_tag if asin_tag else None

                # Check for the title element and extract it if present
                title_element = product.select_one('h2 .a-text-normal')
                if title_element:
                    title = title_element.get_text(strip=True)
                    print(f"Product Title: {title}")  # Print each title to the terminal

                    # Get the current price, convert to float
                    current_price_element = product.select_one('.a-row.a-size-base.a-color-base .a-price .a-offscreen')
                    current_price_text = current_price_element.get_text(strip=True) if current_price_element else None
                    current_price = float(re.sub(r'[^\d.]', '', current_price_text)) if current_price_text else None

                    # Get the original price (before discount), convert to float
                    original_price_element = product.select_one('.a-row.a-size-base.a-color-base .a-price.a-text-price .a-offscreen')
                    original_price_text = original_price_element.get_text(strip=True) if original_price_element else None
                    original_price = float(re.sub(r'[^\d.]', '', original_price_text)) if original_price_text else None

                    # Calculate the discount percentage if original price is available
                    amazon_discount = (100-(current_price / original_price * 100)) if current_price and original_price else None

                    # Extract purchase count text if available
                    purchase_count_element = product.select_one('span.a-size-base.a-color-secondary')
                    purchase_count_text = purchase_count_element.get_text(strip=True) if purchase_count_element else None

                    # Print ASIN, prices, discount, and purchase count to the terminal
                    print(f"ASIN: {asin}, Current Price: {current_price}, Original Price: {original_price}, "
                        f"Discount: {amazon_discount}, Purchase Count: {purchase_count_text}")

                    # Append the product data to the list
                    products.append({
                        'ASIN': asin,
                        'title': title,
                        'current_price': current_price,
                        'original_price': original_price,
                        'amazon_discount': amazon_discount,
                        'purchase_count': purchase_count_text
                    })

                
                # Stop if we've collected the desired number of products
                if len(products) >= num_products:
                    break
            
            page += 1

            # If no products found on the page, break to avoid infinite loop
            if not product_elements:
                print("No more products found.")
                break

    return products

# Asynchronous task to fetch and return data for multiple Amazon product IDs
# Asynchronous task to fetch and return data for Amazon queries
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
                        'ASIN': product.get('ASIN'),
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
            print(f"Query '{query}' returned {len(hits)} products in Dawa.")
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
                
            dawa_data.append({
                'name': hit.get('name', None),
                'price': hit.get('price', {}).get('SAR', {}).get('default', None),
                'price_original': original_price,
                'offer_text_notag': hit.get('offer_text_notag', None),
                'sku': hit.get('sku', None),
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
                    'key': entry.key  # Add 'key' in the final result
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
            print(f"Query '{query}' returned {len(hits)} products.")
            print(f"Query '{query}' returned {len(hits)} products in Nahdi.")
        except aiohttp.ContentTypeError:
            print(f"Failed to fetch data for Nahdi for query '{query}'.")
            response_data = {"results": []}
        return response_data, query

def process_nahdi_response(data, query):
    nahdi_data = []
    for result in data.get('results', []):
        hits = result.get('hits', [])
        for hit in hits:  # Loop through all hits
            # Extract necessary data with default values if not found
            original_price = hit.get('price', {}).get('SAR', {}).get('default_original_formated', None)
            # Remove " SAR" and commas, then convert to float
            if original_price:
                original_price = float(original_price.replace(' SAR', '').replace(',', '').strip())
                
            nahdi_data.append({
                'name': hit.get('name', None),
                'price': hit.get('price', {}).get('SAR', {}).get('default', None),
                'price_original': original_price,
                'ordered_qty': hit.get('ordered_qty', None),
                'sku': hit.get('sku', None),
                'key': query  # Include the query as the key
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
                    'key': entry.key  # Add 'key' in the final result
                })

        return result
