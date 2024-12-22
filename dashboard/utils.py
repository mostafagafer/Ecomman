# import json
# import logging

# from django.core.cache import cache

# def get_cached_data(cache_key, process_function, *args):
#     cached_data = cache.get(cache_key)
#     if cached_data:
#         return cached_data  # Return cached data directly (already JSON serialized)
#     else:
#         data = process_function(*args)
#         serialized_data = json.dumps(data)  # Serialize to JSON for caching
#         cache.set(cache_key, serialized_data, timeout=3600)  # Cache for 1 hour
#         return serialized_data

# def process_data(scraped_data, scraped_bulk_data):
#     # Initialize empty dictionary for data
#     data = {
#         'scraped_at': [],
#         'RSP_VAT': [],
#         'discount_percentage': [],
#         'key_name': [],
#         'amazon_title': [],
#         'nahdi_title': [],
#         'dawa_title': [],
#         'noon_sa_title': [],
#         'amazon_price': [],
#         'nahdi_price': [],
#         'dawa_price': [],
#         'amazon_discount': [],
#         'nahdi_discount': [],
#         'dawa_discount': [],
#         'noon_sa_discount': [],
#         'noon_sa_price': [],
#         'nahdi_ordered_qty': [],
#         'opps': [],
#         'Brand': [],
#         'Category': [],
#         'Subcategory': [],
#         'Product': [],
#         'Account': [],
#         'Competitor': []
#     }

#     # Populate data from `scraped_data`
#     for item in scraped_data:
#         accounts = item.product.accounts_id.all()
#         account_names = [account.name for account in accounts]
#         account_str = ", ".join(account_names) if account_names else None

#         data['scraped_at'].append(item.scraped_at.isoformat() if item.scraped_at else None)
#         data['RSP_VAT'].append(item.product.RSP_VAT if item.product.RSP_VAT is not None else None)
#         data['discount_percentage'].append(item.discount_percentage if item.discount_percentage is not None else None)
#         data['key_name'].append(None)
#         data['amazon_title'].append(item.amazon_title)
#         data['nahdi_title'].append(item.nahdi_title)
#         data['dawa_title'].append(item.dawa_title)
#         data['noon_sa_title'].append(item.noon_sa_title)
#         data['amazon_price'].append(item.amazon_price)
#         data['nahdi_price'].append(item.nahdi_price)
#         data['dawa_price'].append(item.dawa_price)
#         data['amazon_discount'].append(item.amazon_discount)
#         data['nahdi_discount'].append(item.nahdi_discount)
#         data['dawa_discount'].append(item.dawa_discount)
#         data['noon_sa_discount'].append(item.noon_sa_discount)
#         data['noon_sa_price'].append(item.noon_sa_price if item.noon_sa_price else 0)
#         data['nahdi_ordered_qty'].append(item.nahdi_ordered_qty)
#         data['opps'].append(item.opps)
#         data['Brand'].append(str(item.product.brand) if item.product.brand else None)
#         data['Category'].append(str(item.product.category) if item.product.category else None)
#         data['Subcategory'].append(str(item.product.subcategory) if item.product.subcategory else None)
#         data['Product'].append(item.product.TITLE)
#         data['Account'].append(account_str)
#         data['Competitor'].append(item.product.is_competitor)

#     # Populate data from `scraped_bulk_data`
#     for bulk_item in scraped_bulk_data:
#         data['scraped_at'].append(bulk_item.scraped_at.isoformat() if bulk_item.scraped_at else None)
#         data['RSP_VAT'].append(None)
#         data['discount_percentage'].append(None)
#         data['key_name'].append(bulk_item.key_name)
#         data['amazon_title'].append(bulk_item.amazon_title)
#         data['nahdi_title'].append(bulk_item.nahdi_title)
#         data['dawa_title'].append(bulk_item.dawa_title)
#         data['noon_sa_title'].append(bulk_item.noon_sa_title)
#         data['amazon_price'].append(bulk_item.amazon_price)
#         data['nahdi_price'].append(bulk_item.nahdi_price)
#         data['dawa_price'].append(bulk_item.dawa_price)
#         data['amazon_discount'].append(bulk_item.amazon_discount)
#         data['nahdi_discount'].append(bulk_item.nahdi_discount)
#         data['dawa_discount'].append(bulk_item.dawa_discount)
#         data['noon_sa_discount'].append(bulk_item.noon_sa_discount)
#         data['noon_sa_price'].append(bulk_item.noon_sa_price if bulk_item.noon_sa_price else 0)
#         data['nahdi_ordered_qty'].append(bulk_item.nahdi_ordered_qty)
#         data['opps'].append(None)
#         data['Brand'].append(None)
#         data['Category'].append(None)
#         data['Subcategory'].append(None)
#         data['Product'].append(None)
#         data['Account'].append(None)
#         data['Competitor'].append(item.product.is_competitor)
    
#     # Align lengths of all lists
#     min_length = min(len(values) for values in data.values())
#     if min_length == 0:
#         raise ValueError("No data to process from scraped_data or scraped_bulk_data.")

#     data = {key: values[:min_length] for key, values in data.items()}

#     return data


def process_data(scraped_data, scraped_bulk_data):
    # logger = logging.getLogger(__name__)

    # Initialize empty dictionary for data
    data = {
        'scraped_at': [],
        'RSP_VAT': [],
        'discount_percentage': [],
        'key_name': [],
        'amazon_title': [],
        'nahdi_title': [],
        'dawa_title': [],
        'noon_sa_title': [],
        'amazon_price': [],
        'nahdi_price': [],
        'dawa_price': [],
        'amazon_discount': [],
        'nahdi_discount': [],
        'dawa_discount': [],
        'noon_sa_discount': [],
        'noon_sa_price': [],
        'nahdi_ordered_qty': [],
        'opps': [],
        'account_deviation_score':[],
        'price_deviation_score':[],
        'Brand': [],
        'Category': [],
        'Subcategory': [],
        'Product': [],
        'Account': [],
        'Competitor': []
    }

    # Populate data from `scraped_data`
    for item in scraped_data:
        accounts = item.product.accounts_id.all()
        account_names = [str(account.name) for account in accounts]  # Convert to string
        account_str = ", ".join(account_names) if account_names else None

        # logger.info(f"Processing scraped_data item: {item}")

        data['scraped_at'].append(item.scraped_at.isoformat() if item.scraped_at else None)  # Convert datetime to ISO
        data['RSP_VAT'].append(float(item.product.RSP_VAT) if item.product.RSP_VAT is not None else None)
        data['discount_percentage'].append(float(item.discount_percentage) if item.discount_percentage is not None else None)
        data['key_name'].append(None)
        data['amazon_title'].append(str(item.amazon_title))
        data['nahdi_title'].append(str(item.nahdi_title))
        data['dawa_title'].append(str(item.dawa_title))
        data['noon_sa_title'].append(str(item.noon_sa_title))
        data['amazon_price'].append(float(item.amazon_price) if item.amazon_price is not None else None)
        data['nahdi_price'].append(float(item.nahdi_price) if item.nahdi_price is not None else None)
        data['dawa_price'].append(float(item.dawa_price) if item.dawa_price is not None else None)
        data['amazon_discount'].append(float(item.amazon_discount) if item.amazon_discount is not None else None)
        data['nahdi_discount'].append(float(item.nahdi_discount) if item.nahdi_discount is not None else None)
        data['dawa_discount'].append(float(item.dawa_discount) if item.dawa_discount is not None else None)
        data['noon_sa_discount'].append(float(item.noon_sa_discount) if item.noon_sa_discount is not None else None)
        data['noon_sa_price'].append(float(item.noon_sa_price) if item.noon_sa_price is not None else None)
        data['nahdi_ordered_qty'].append(int(item.nahdi_ordered_qty) if item.nahdi_ordered_qty is not None else None)
        data['opps'].append(float(item.opps) if item.opps is not None else None)
        data['account_deviation_score'].append(float(item.account_deviation_score) if item.account_deviation_score is not None else None)
        data['price_deviation_score'].append(float(item.price_deviation_score) if item.price_deviation_score is not None else None)
        data['Brand'].append(str(item.product.brand) if item.product.brand else None)
        data['Category'].append(str(item.product.category) if item.product.category else None)
        data['Subcategory'].append(str(item.product.subcategory) if item.product.subcategory else None)
        data['Product'].append(str(item.product.TITLE))
        data['Account'].append(account_str)
        data['Competitor'].append(str(item.product.is_competitor))

    # Populate data from `scraped_bulk_data`
    for bulk_item in scraped_bulk_data:
        # logger.info(f"Processing scraped_bulk_data item: {bulk_item}")

        data['scraped_at'].append(bulk_item.scraped_at.isoformat() if bulk_item.scraped_at else None)
        data['RSP_VAT'].append(None)
        data['discount_percentage'].append(None)
        data['key_name'].append(str(bulk_item.key_name) if bulk_item.key_name else None)
        data['amazon_title'].append(str(bulk_item.amazon_title) if bulk_item.amazon_title else None)
        data['nahdi_title'].append(str(bulk_item.nahdi_title) if bulk_item.nahdi_title else None)
        data['dawa_title'].append(str(bulk_item.dawa_title) if bulk_item.dawa_title else None)
        data['noon_sa_title'].append(str(bulk_item.noon_sa_title) if bulk_item.noon_sa_title else None)
        data['amazon_price'].append(float(bulk_item.amazon_price) if bulk_item.amazon_price is not None else None)
        data['nahdi_price'].append(float(bulk_item.nahdi_price) if bulk_item.nahdi_price is not None else None)
        data['dawa_price'].append(float(bulk_item.dawa_price) if bulk_item.dawa_price is not None else None)
        data['amazon_discount'].append(float(bulk_item.amazon_discount) if bulk_item.amazon_discount is not None else None)
        data['nahdi_discount'].append(float(bulk_item.nahdi_discount) if bulk_item.nahdi_discount is not None else None)
        data['dawa_discount'].append(float(bulk_item.dawa_discount) if bulk_item.dawa_discount is not None else None)
        data['noon_sa_discount'].append(float(bulk_item.noon_sa_discount) if bulk_item.noon_sa_discount is not None else None)
        data['noon_sa_price'].append(float(bulk_item.noon_sa_price) if bulk_item.noon_sa_price is not None else None)
        data['nahdi_ordered_qty'].append(int(bulk_item.nahdi_ordered_qty) if bulk_item.nahdi_ordered_qty is not None else None)
        data['opps'].append(None)
        data['account_deviation_score'].append(None)
        data['price_deviation_score'].append(None)
        data['Brand'].append(None)
        data['Category'].append(None)
        data['Subcategory'].append(None)
        data['Product'].append(None)
        data['Account'].append(None)
        data['Competitor'].append(None)

    # Align lengths of all lists
    min_length = min(len(values) for values in data.values())
    if min_length == 0:
        raise ValueError("No data to process from scraped_data or scraped_bulk_data.")

    data = {key: values[:min_length] for key, values in data.items()}

    return data
