
# import math
# import json
# import zlib
# from datetime import datetime, timedelta
import pandas as pd
from django.db import connection
# from .materialized_views import create_materialized_view  # Adjust import path as needed


def get_materialized_view_data(period):
    """Fetch data from the appropriate materialized view based on period selection"""
    if period == "last_week":
        view_name = "last_7_days_view"  # Adjust to your actual view name
    elif period == "last_month":
        view_name = "last_30_days_view"  # Adjust to your actual view name
    else:
        raise ValueError("Invalid period selected")
    
    # Fetch data from the materialized view using Django ORM
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {view_name};")
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(data, columns=columns)
    return df


# def process_data(scraped_data, scraped_bulk_data):
#     print("Starting process_data...")

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
#         'account_deviation_score': [],
#         'price_deviation_score': [],
#         'Brand': [],
#         'Category': [],
#         'Subcategory': [],
#         'Product': [],
#         'Account': [],
#         'Competitor': [],
#         'Competitor_Ref': [],  # New field for competitor references
#         'bulk_df': []  # Flag for bulk_df
#     }

#     # Populate data from `scraped_data`
#     print("Processing scraped_data...")
#     for item in scraped_data:
#         accounts = item.product.accounts_id.all()
#         account_names = [str(account.name) for account in accounts]  # Convert to string
#         account_str = ", ".join(account_names) if account_names else None

#         # Fetch competitor references for the product
#         competitor_refs = item.product.competitor_references.all()
#         competitor_ref_titles = [ref.TITLE for ref in competitor_refs]  # Extract competitor titles as a list

#         data['scraped_at'].append(item.scraped_at.isoformat() if item.scraped_at else None)  # Convert datetime to ISO
#         data['RSP_VAT'].append(float(item.product.RSP_VAT) if item.product.RSP_VAT is not None else None)
#         data['discount_percentage'].append(float(item.discount_percentage) if item.discount_percentage is not None else None)
#         data['key_name'].append(None)
#         data['amazon_title'].append(str(item.amazon_title))
#         data['nahdi_title'].append(str(item.nahdi_title))
#         data['dawa_title'].append(str(item.dawa_title))
#         data['noon_sa_title'].append(str(item.noon_sa_title))
#         data['amazon_price'].append(float(item.amazon_price) if item.amazon_price is not None else None)
#         data['nahdi_price'].append(float(item.nahdi_price) if item.nahdi_price is not None else None)
#         data['dawa_price'].append(float(item.dawa_price) if item.dawa_price is not None else None)
#         data['amazon_discount'].append(float(item.amazon_discount) if item.amazon_discount is not None else None)
#         data['nahdi_discount'].append(float(item.nahdi_discount) if item.nahdi_discount is not None else None)
#         data['dawa_discount'].append(float(item.dawa_discount) if item.dawa_discount is not None else None)
#         data['noon_sa_discount'].append(float(item.noon_sa_discount) if item.noon_sa_discount is not None else None)
#         data['noon_sa_price'].append(float(item.noon_sa_price) if item.noon_sa_price is not None else None)
#         data['nahdi_ordered_qty'].append(
#             int(item.nahdi_ordered_qty) if item.nahdi_ordered_qty is not None and not math.isnan(item.nahdi_ordered_qty) else None
#         )
#         data['opps'].append(float(item.opps) if item.opps is not None else None)
#         data['account_deviation_score'].append(float(item.account_deviation_score) if item.account_deviation_score is not None else None)
#         data['price_deviation_score'].append(float(item.price_deviation_score) if item.price_deviation_score is not None else None)
#         data['Brand'].append(str(item.product.brand) if item.product.brand else None)
#         data['Category'].append(str(item.product.category) if item.product.category else None)
#         data['Subcategory'].append(str(item.product.subcategory) if item.product.subcategory else None)
#         data['Product'].append(str(item.product.TITLE))
#         data['Account'].append(account_str)
#         data['Competitor'].append(str(item.product.is_competitor))
#         data['Competitor_Ref'].append(competitor_ref_titles)  # Add competitor references as a list
#         data['bulk_df'].append(0)  # Flag for scraped_data

#     # Populate data from `scraped_bulk_data`
#     print("Processing scraped_bulk_data...")
#     for bulk_item in scraped_bulk_data:
#         # Coalesce titles into a single 'Product' column
#         product_name = (
#             bulk_item.amazon_title or
#             bulk_item.dawa_title or
#             bulk_item.nahdi_title or
#             bulk_item.noon_sa_title
#         )

#         data['scraped_at'].append(bulk_item.scraped_at.isoformat() if bulk_item.scraped_at else None)
#         data['RSP_VAT'].append(None)
#         data['discount_percentage'].append(None)
#         data['key_name'].append(str(bulk_item.key_name) if bulk_item.key_name else None)
#         data['amazon_title'].append(str(bulk_item.amazon_title) if bulk_item.amazon_title else None)
#         data['nahdi_title'].append(str(bulk_item.nahdi_title) if bulk_item.nahdi_title else None)
#         data['dawa_title'].append(str(bulk_item.dawa_title) if bulk_item.dawa_title else None)
#         data['noon_sa_title'].append(str(bulk_item.noon_sa_title) if bulk_item.noon_sa_title else None)
#         data['amazon_price'].append(float(bulk_item.amazon_price) if bulk_item.amazon_price is not None else None)
#         data['nahdi_price'].append(float(bulk_item.nahdi_price) if bulk_item.nahdi_price is not None else None)
#         data['dawa_price'].append(float(bulk_item.dawa_price) if bulk_item.dawa_price is not None else None)
#         data['amazon_discount'].append(float(bulk_item.amazon_discount) if bulk_item.amazon_discount is not None else None)
#         data['nahdi_discount'].append(float(bulk_item.nahdi_discount) if bulk_item.nahdi_discount is not None else None)
#         data['dawa_discount'].append(float(bulk_item.dawa_discount) if bulk_item.dawa_discount is not None else None)
#         data['noon_sa_discount'].append(float(bulk_item.noon_sa_discount) if bulk_item.noon_sa_discount is not None else None)
#         data['noon_sa_price'].append(float(bulk_item.noon_sa_price) if bulk_item.noon_sa_price is not None else None)
#         data['nahdi_ordered_qty'].append(
#             int(bulk_item.nahdi_ordered_qty) if bulk_item.nahdi_ordered_qty is not None and not math.isnan(bulk_item.nahdi_ordered_qty) else None
#         )
#         data['opps'].append(None)
#         data['account_deviation_score'].append(None)
#         data['price_deviation_score'].append(None)
#         data['Brand'].append(None)
#         data['Category'].append(None)
#         data['Subcategory'].append(None)
#         data['Product'].append(product_name)
#         data['Account'].append(None)
#         data['Competitor'].append(None)
#         data['Competitor_Ref'].append(None)  # Add competitor references as a list
#         data['bulk_df'].append(1)  # Flag for bulk_df

#     # Align lengths of all lists
#     min_length = min(len(values) for values in data.values())
#     if min_length == 0:
#         raise ValueError("No data to process from scraped_data or scraped_bulk_data.")

#     data = {key: values[:min_length] for key, values in data.items()}

#     # Convert data to DataFrame
#     df = pd.DataFrame(data)
#     df['scraped_at'] = pd.to_datetime(df['scraped_at'])

#     # Get the current date and time (make it timezone-aware)
#     now = datetime.now().replace(tzinfo=None)  # Ensure `now` is timezone-naive
#     df['scraped_at'] = df['scraped_at'].dt.tz_localize(None)  # Ensure `scraped_at` is timezone-naive

#     # Precompute data for each period
#     precomputed_data = {}

#     # Last Week (14 rows per product, aggregated daily)
#     print("Precomputing last_week data...")
#     last_week_start = now - timedelta(days=7)
#     last_week_df = df[df['scraped_at'] >= last_week_start]
#     last_week_df = last_week_df.groupby(['Product', pd.Grouper(key='scraped_at', freq='D')]).agg({
#         'amazon_price': 'mean',
#         'nahdi_price': 'mean',
#         'dawa_price': 'mean',
#         'noon_sa_price': 'mean',
#         'amazon_discount': 'mean',
#         'nahdi_discount': 'mean',
#         'dawa_discount': 'mean',
#         'noon_sa_discount': 'mean',
#         'RSP_VAT': 'mean',
#         'discount_percentage': 'mean',
#         'opps': 'mean',
#         'nahdi_ordered_qty': 'max',
#         'amazon_title': 'last',  # Take the last value for string columns
#         'dawa_title': 'last',
#         'nahdi_title': 'last',
#         'noon_sa_title': 'last',
#         'key_name': 'last',
#         'Brand': 'last',
#         'Category': 'last',
#         'Subcategory': 'last',
#         'Competitor': 'last',
#         'Competitor_Ref': lambda x: x.iloc[0],  # Preserve the list of competitor references
#     }).reset_index()
#     precomputed_data['last_week'] = last_week_df

#     # Last Month (30 rows per product, aggregated daily)
#     print("Precomputing last_month data...")
#     last_month_start = now - timedelta(days=30)
#     last_month_df = df[df['scraped_at'] >= last_month_start]
#     last_month_df = last_month_df.groupby(['Product', pd.Grouper(key='scraped_at', freq='D')]).agg({
#         'amazon_price': 'mean',
#         'nahdi_price': 'mean',
#         'dawa_price': 'mean',
#         'noon_sa_price': 'mean',
#         'amazon_discount': 'mean',
#         'nahdi_discount': 'mean',
#         'dawa_discount': 'mean',
#         'noon_sa_discount': 'mean',
#         'RSP_VAT': 'mean',
#         'discount_percentage': 'mean',
#         'opps': 'mean',
#         'nahdi_ordered_qty': 'max',
#         'amazon_title': 'last',  # Take the last value for string columns
#         'dawa_title': 'last',
#         'nahdi_title': 'last',
#         'noon_sa_title': 'last',
#         'key_name': 'last',
#         'Brand': 'last',
#         'Category': 'last',
#         'Subcategory': 'last',
#         'Competitor': 'last',
#         'Competitor_Ref': lambda x: x.iloc[0],  # Preserve the list of competitor references
#     }).reset_index()
#     precomputed_data['last_month'] = last_month_df

#     # Last 6 Months (weekly aggregation starting on Sunday)
#     print("Precomputing last_6_months data...")
#     last_6_months_start = now - timedelta(days=180)
#     last_6_months_df = df[df['scraped_at'] >= last_6_months_start]
#     last_6_months_df['week_start'] = last_6_months_df['scraped_at'] - pd.to_timedelta(last_6_months_df['scraped_at'].dt.weekday, unit='d')
#     last_6_months_df = last_6_months_df.groupby(['Product', 'week_start']).agg({
#         'amazon_price': 'mean',
#         'nahdi_price': 'mean',
#         'dawa_price': 'mean',
#         'noon_sa_price': 'mean',
#         'amazon_discount': 'mean',
#         'nahdi_discount': 'mean',
#         'dawa_discount': 'mean',
#         'noon_sa_discount': 'mean',
#         'RSP_VAT': 'mean',
#         'discount_percentage': 'mean',
#         'opps': 'mean',
#         'nahdi_ordered_qty': 'max',
#         'amazon_title': 'last',  # Take the last value for string columns
#         'dawa_title': 'last',
#         'nahdi_title': 'last',
#         'noon_sa_title': 'last',
#         'key_name': 'last',
#         'Brand': 'last',
#         'Category': 'last',
#         'Subcategory': 'last',
#         'Competitor': 'last',
#         'Competitor_Ref': lambda x: x.iloc[0],  # Preserve the list of competitor references
#     }).reset_index()
#     precomputed_data['last_6_months'] = last_6_months_df

#     # Last Year (12 rows per product, aggregated monthly)
#     print("Precomputing last_year data...")
#     last_year_start = now - timedelta(days=365)
#     last_year_df = df[df['scraped_at'] >= last_year_start]
#     last_year_df = last_year_df.groupby(['Product', pd.Grouper(key='scraped_at', freq='ME')]).agg({
#         'amazon_price': 'mean',
#         'nahdi_price': 'mean',
#         'dawa_price': 'mean',
#         'noon_sa_price': 'mean',
#         'amazon_discount': 'mean',
#         'nahdi_discount': 'mean',
#         'dawa_discount': 'mean',
#         'noon_sa_discount': 'mean',
#         'RSP_VAT': 'mean',
#         'discount_percentage': 'mean',
#         'opps': 'mean',
#         'nahdi_ordered_qty': 'max',
#         'amazon_title': 'last',  # Take the last value for string columns
#         'dawa_title': 'last',
#         'nahdi_title': 'last',
#         'noon_sa_title': 'last',
#         'key_name': 'last',
#         'Brand': 'last',
#         'Category': 'last',
#         'Subcategory': 'last',
#         'Competitor': 'last',
#         'Competitor_Ref': lambda x: x.iloc[0],  # Preserve the list of competitor references
#     }).reset_index()
#     precomputed_data['last_year'] = last_year_df

#     # Year-to-Date (YTD) (monthly aggregation)
#     print("Precomputing ytd data...")
#     ytd_start = datetime(now.year, 1, 1)
#     ytd_df = df[df['scraped_at'] >= ytd_start]
#     ytd_df = ytd_df.groupby(['Product', pd.Grouper(key='scraped_at', freq='ME')]).agg({
#         'amazon_price': 'mean',
#         'nahdi_price': 'mean',
#         'dawa_price': 'mean',
#         'noon_sa_price': 'mean',
#         'amazon_discount': 'mean',
#         'nahdi_discount': 'mean',
#         'dawa_discount': 'mean',
#         'noon_sa_discount': 'mean',
#         'RSP_VAT': 'mean',
#         'discount_percentage': 'mean',
#         'opps': 'mean',
#         'nahdi_ordered_qty': 'max',
#         'amazon_title': 'last',  # Take the last value for string columns
#         'dawa_title': 'last',
#         'nahdi_title': 'last',
#         'noon_sa_title': 'last',
#         'key_name': 'last',
#         'Brand': 'last',
#         'Category': 'last',
#         'Subcategory': 'last',
#         'Competitor': 'last',
#         'Competitor_Ref': lambda x: x.iloc[0],  # Preserve the list of competitor references
#     }).reset_index()
#     precomputed_data['ytd'] = ytd_df

#     # After aggregating each DataFrame, convert Timestamp columns to strings
#     for key in precomputed_data:
#         if 'scraped_at' in precomputed_data[key].columns:
#             precomputed_data[key]['scraped_at'] = precomputed_data[key]['scraped_at'].astype(str)
#         if 'week_start' in precomputed_data[key].columns:
#             precomputed_data[key]['week_start'] = precomputed_data[key]['week_start'].astype(str)

#     print("process_data completed successfully.")
#     # Convert each DataFrame in precomputed_data to a dictionary
#     for key in precomputed_data:
#         precomputed_data[key] = precomputed_data[key].to_dict('records')

#     # Serialize the precomputed_data dictionary to a JSON string
#     serialized_data = json.dumps(precomputed_data)

#     # Compress the serialized data into bytes
#     compressed_data = zlib.compress(serialized_data.encode('utf-8'))

#     return compressed_data


# Old function changed on 14/Jan
# def process_data(scraped_data, scraped_bulk_data):
#     # logger = logging.getLogger(__name__)

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
#         'account_deviation_score':[],
#         'price_deviation_score':[],
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
#         account_names = [str(account.name) for account in accounts]  # Convert to string
#         account_str = ", ".join(account_names) if account_names else None

#         # logger.info(f"Processing scraped_data item: {item}")

#         data['scraped_at'].append(item.scraped_at.isoformat() if item.scraped_at else None)  # Convert datetime to ISO
#         data['RSP_VAT'].append(float(item.product.RSP_VAT) if item.product.RSP_VAT is not None else None)
#         data['discount_percentage'].append(float(item.discount_percentage) if item.discount_percentage is not None else None)
#         data['key_name'].append(None)
#         data['amazon_title'].append(str(item.amazon_title))
#         data['nahdi_title'].append(str(item.nahdi_title))
#         data['dawa_title'].append(str(item.dawa_title))
#         data['noon_sa_title'].append(str(item.noon_sa_title))
#         data['amazon_price'].append(float(item.amazon_price) if item.amazon_price is not None else None)
#         data['nahdi_price'].append(float(item.nahdi_price) if item.nahdi_price is not None else None)
#         data['dawa_price'].append(float(item.dawa_price) if item.dawa_price is not None else None)
#         data['amazon_discount'].append(float(item.amazon_discount) if item.amazon_discount is not None else None)
#         data['nahdi_discount'].append(float(item.nahdi_discount) if item.nahdi_discount is not None else None)
#         data['dawa_discount'].append(float(item.dawa_discount) if item.dawa_discount is not None else None)
#         data['noon_sa_discount'].append(float(item.noon_sa_discount) if item.noon_sa_discount is not None else None)
#         data['noon_sa_price'].append(float(item.noon_sa_price) if item.noon_sa_price is not None else None)
#         # data['nahdi_ordered_qty'].append(int(item.nahdi_ordered_qty) if item.nahdi_ordered_qty is not None else None)
#         data['nahdi_ordered_qty'].append(
#     int(item.nahdi_ordered_qty) if item.nahdi_ordered_qty is not None and not math.isnan(item.nahdi_ordered_qty) else None
# )

#         data['opps'].append(float(item.opps) if item.opps is not None else None)
#         data['account_deviation_score'].append(float(item.account_deviation_score) if item.account_deviation_score is not None else None)
#         data['price_deviation_score'].append(float(item.price_deviation_score) if item.price_deviation_score is not None else None)
#         data['Brand'].append(str(item.product.brand) if item.product.brand else None)
#         data['Category'].append(str(item.product.category) if item.product.category else None)
#         data['Subcategory'].append(str(item.product.subcategory) if item.product.subcategory else None)
#         data['Product'].append(str(item.product.TITLE))
#         data['Account'].append(account_str)
#         data['Competitor'].append(str(item.product.is_competitor))

#     # Populate data from `scraped_bulk_data`
#     for bulk_item in scraped_bulk_data:
#         # logger.info(f"Processing scraped_bulk_data item: {bulk_item}")

#         data['scraped_at'].append(bulk_item.scraped_at.isoformat() if bulk_item.scraped_at else None)
#         data['RSP_VAT'].append(None)
#         data['discount_percentage'].append(None)
#         data['key_name'].append(str(bulk_item.key_name) if bulk_item.key_name else None)
#         data['amazon_title'].append(str(bulk_item.amazon_title) if bulk_item.amazon_title else None)
#         data['nahdi_title'].append(str(bulk_item.nahdi_title) if bulk_item.nahdi_title else None)
#         data['dawa_title'].append(str(bulk_item.dawa_title) if bulk_item.dawa_title else None)
#         data['noon_sa_title'].append(str(bulk_item.noon_sa_title) if bulk_item.noon_sa_title else None)
#         data['amazon_price'].append(float(bulk_item.amazon_price) if bulk_item.amazon_price is not None else None)
#         data['nahdi_price'].append(float(bulk_item.nahdi_price) if bulk_item.nahdi_price is not None else None)
#         data['dawa_price'].append(float(bulk_item.dawa_price) if bulk_item.dawa_price is not None else None)
#         data['amazon_discount'].append(float(bulk_item.amazon_discount) if bulk_item.amazon_discount is not None else None)
#         data['nahdi_discount'].append(float(bulk_item.nahdi_discount) if bulk_item.nahdi_discount is not None else None)
#         data['dawa_discount'].append(float(bulk_item.dawa_discount) if bulk_item.dawa_discount is not None else None)
#         data['noon_sa_discount'].append(float(bulk_item.noon_sa_discount) if bulk_item.noon_sa_discount is not None else None)
#         data['noon_sa_price'].append(float(bulk_item.noon_sa_price) if bulk_item.noon_sa_price is not None else None)
#         # data['nahdi_ordered_qty'].append(int(bulk_item.nahdi_ordered_qty) if bulk_item.nahdi_ordered_qty is not None else None)
#         data['nahdi_ordered_qty'].append(
#     int(bulk_item.nahdi_ordered_qty) if bulk_item.nahdi_ordered_qty is not None and not math.isnan(bulk_item.nahdi_ordered_qty) else None
# )
#         data['opps'].append(None)
#         data['account_deviation_score'].append(None)
#         data['price_deviation_score'].append(None)
#         data['Brand'].append(None)
#         data['Category'].append(None)
#         data['Subcategory'].append(None)
#         data['Product'].append(None)
#         data['Account'].append(None)
#         data['Competitor'].append(None)

#     # Align lengths of all lists
#     min_length = min(len(values) for values in data.values())
#     if min_length == 0:
#         raise ValueError("No data to process from scraped_data or scraped_bulk_data.")

#     data = {key: values[:min_length] for key, values in data.items()}

#     return data
