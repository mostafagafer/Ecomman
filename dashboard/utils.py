import json
from django.core.cache import cache

def get_cached_data(cache_key, process_function, *args):
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data  # Return cached data directly (already JSON serialized)
    else:
        data = process_function(*args)
        serialized_data = json.dumps(data)  # Serialize to JSON for caching
        cache.set(cache_key, serialized_data, timeout=3600)  # Cache for 1 hour
        return serialized_data

def process_data(scraped_data, scraped_bulk_data):
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
        'Brand': [],
        'Category': [],
        'Subcategory': [],
        'Product': [],
        'Account': []
    }

    # Populate data from `scraped_data`
    for item in scraped_data:
        accounts = item.product.accounts_id.all()
        account_names = [account.name for account in accounts]
        account_str = ", ".join(account_names) if account_names else None

        data['scraped_at'].append(item.scraped_at.isoformat() if item.scraped_at else None)
        data['RSP_VAT'].append(item.product.RSP_VAT if item.product.RSP_VAT is not None else None)
        data['discount_percentage'].append(item.discount_percentage if item.discount_percentage is not None else None)
        data['key_name'].append(None)
        data['amazon_title'].append(item.amazon_title)
        data['nahdi_title'].append(item.nahdi_title)
        data['dawa_title'].append(item.dawa_title)
        data['noon_sa_title'].append(item.noon_sa_title)
        data['amazon_price'].append(item.amazon_price)
        data['nahdi_price'].append(item.nahdi_price)
        data['dawa_price'].append(item.dawa_price)
        data['amazon_discount'].append(item.amazon_discount)
        data['nahdi_discount'].append(item.nahdi_discount)
        data['dawa_discount'].append(item.dawa_discount)
        data['noon_sa_discount'].append(item.noon_sa_discount)
        data['noon_sa_price'].append(item.noon_sa_price if item.noon_sa_price else 0)
        data['nahdi_ordered_qty'].append(item.nahdi_ordered_qty)
        data['opps'].append(item.opps)
        data['Brand'].append(str(item.product.brand) if item.product.brand else None)
        data['Category'].append(str(item.product.category) if item.product.category else None)
        data['Subcategory'].append(str(item.product.subcategory) if item.product.subcategory else None)
        data['Product'].append(item.product.TITLE)
        data['Account'].append(account_str)

    # Populate data from `scraped_bulk_data`
    for bulk_item in scraped_bulk_data:
        data['scraped_at'].append(bulk_item.scraped_at.isoformat() if bulk_item.scraped_at else None)
        data['RSP_VAT'].append(None)
        data['discount_percentage'].append(None)
        data['key_name'].append(bulk_item.key_name)
        data['amazon_title'].append(bulk_item.amazon_title)
        data['nahdi_title'].append(bulk_item.nahdi_title)
        data['dawa_title'].append(bulk_item.dawa_title)
        data['noon_sa_title'].append(bulk_item.noon_sa_title)
        data['amazon_price'].append(bulk_item.amazon_price)
        data['nahdi_price'].append(bulk_item.nahdi_price)
        data['dawa_price'].append(bulk_item.dawa_price)
        data['amazon_discount'].append(bulk_item.amazon_discount)
        data['nahdi_discount'].append(bulk_item.nahdi_discount)
        data['dawa_discount'].append(bulk_item.dawa_discount)
        data['noon_sa_discount'].append(bulk_item.noon_sa_discount)
        data['noon_sa_price'].append(bulk_item.noon_sa_price if bulk_item.noon_sa_price else 0)
        data['nahdi_ordered_qty'].append(bulk_item.nahdi_ordered_qty)
        data['opps'].append(None)
        data['Brand'].append(None)
        data['Category'].append(None)
        data['Subcategory'].append(None)
        data['Product'].append(None)
        data['Account'].append(None)

    # Align lengths of all lists
    min_length = min(len(values) for values in data.values())
    if min_length == 0:
        raise ValueError("No data to process from scraped_data or scraped_bulk_data.")

    data = {key: values[:min_length] for key, values in data.items()}

    return data
