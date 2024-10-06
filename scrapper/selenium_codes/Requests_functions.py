from bs4 import BeautifulSoup
import aiohttp
import asyncio
import json


# Function to fetch and parse Amazon product details asynchronously
async def fetch_amazon_product(session, product_id):
    url = f'https://www.amazon.sa/dp/{product_id}'
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

    try:
        async with session.get(url, headers=headers) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract the price
            price_element = soup.find(class_='reinventPricePriceToPayMargin')
            price = price_element.get_text(strip=True).replace("\n", ".").replace("SAR", "").strip() if price_element else None

            # Extract shipping info
            ship_element = soup.find(class_='offer-display-feature-text-message')
            shipping_info = ship_element.get_text(strip=True) if ship_element else None

            # Extract 'Sold By' info (if available)
            sold_by_elements = soup.find_all(class_='offer-display-feature-text-message')
            sold_by_info = sold_by_elements[1].get_text(strip=True) if len(sold_by_elements) > 1 else None

            return price, shipping_info, sold_by_info

    except Exception as e:
        print(f"Error fetching data for {product_id}: {e}")
        return None, None, None

# Asynchronous task to fetch and return data for multiple Amazon product IDs
async def get_amazon_product_details(product_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_amazon_product(session, product_id) for product_id in product_ids]
        
        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)
        
        # Unzip the responses into separate lists
        prices_amazon, amazon_shipping, amazon_sold = map(list, zip(*responses))
        
        return prices_amazon, amazon_shipping, amazon_sold

async def fetch_nahdi_data(session, query):
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
                f"&hitsPerPage=20&maxValuesPerFacet=100&numericFilters=%5B%22visibility_search%3D1%22%5D"
                f"&page=0&query={query}&ruleContexts=%5B%22magento_filters%22%5D&tagFilters="
            )
        }]
    }
    
    async with session.post(url, json=payload, headers=headers) as response:
        try:
            response_data = await response.json()
        except aiohttp.ContentTypeError:
            response_data = {"results": []}
        return response_data

# Process the Nahdi response to extract prices
def process_nahdi_response(data):
    prices = []
    for result in data.get('results', []):
        for hit in result.get('hits', []):
            price = hit.get('price', {}).get('SAR', {}).get('default')
            prices.append(price)
    return prices

# Asynchronous task to fetch and return data for multiple SKUs
async def get_nahdi_prices(nahdi_queries):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_nahdi_data(session, query) for query in nahdi_queries]
        
        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)

        # Process responses to extract prices
        all_prices = [process_nahdi_response(response) for response in responses]
        return [price[0] if price else None for price in all_prices]

# Fetch Dawa Data Asynchronously
async def fetch_dawa_data(session, query):
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
                f"&ruleContexts=%5B%22magento_filters%22%5D&hitsPerPage=12&clickAnalytics=true"
                f"&query={query}&maxValuesPerFacet=10"
                f"&facets=%5B%22brand%22%2C%22diaper_size%22%2C%22features%22%2C%22product_function%22"
                f"%2C%22duration%22%2C%22gender%22%2C%22package%22%2C%22product_form%22%2C%22area_covered%22"
                f"%2C%22color%22%2C%22skin_concern%22%2C%22age%22%2C%22volume%22%2C%22ingredients%22%2C%22scent%22"
                f"%2C%22hair_type%22%2C%22skin_type%22%2C%22diaper_number%22%2C%22milk_number%22%2C%22price.SAR.default%22"
                f"%2C%22categories.level0%22%5D&tagFilters=&numericFilters=%5B%22visibility_search%3D1%22%5D"
            )
        }]
    }

    async with session.post(url, json=payload, headers=headers) as response:
        try:
            response_data = await response.json()
        except aiohttp.ContentTypeError:
            response_data = {"results": []}
        return response_data

# Process the Dawa response to extract prices
def process_dawa_response(data):
    prices = []
    for result in data.get('results', []):
        for hit in result.get('hits', []):
            price = hit.get('price', {}).get('SAR', {}).get('default')
            prices.append(price)
    return prices

# Asynchronous task to fetch and return data for multiple queries
async def get_dawa_prices(dawa_queries):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_dawa_data(session, query) for query in dawa_queries]
        
        # Wait for all tasks to complete
        responses = await asyncio.gather(*tasks)

        # Process responses to extract prices
        all_prices = [process_dawa_response(response) for response in responses]
        return [price[0] if price else None for price in all_prices]  # Select the first price if multiple
