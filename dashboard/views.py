from django.shortcuts import render, redirect
from scrapper.models import ScrapedData, ScrapedBulkData
from client_profile.models import Profile, PinnedTable, Brand ,Product, Subcategory, PromoPlan
# from django.db.models import OuterRef, Subquery, Max, F, Value as V, FloatField
from django.db.models import OuterRef, Max, Subquery
from django.contrib.auth.decorators import login_required
# from django.db.models.functions import Coalesce
from .dash_apps.app import plot_dashboard
import pandas as pd
from scrapper.tasks import scrape_user_products_task, scrape_user_Bulk_product_task
from dashboard.tasks import cache_user_data
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from io import BytesIO
import logging
# from dashboard.utils import process_data, get_cached_data
import json
from django.core.cache import cache

# Initialize logger
logger = logging.getLogger(__name__)


@login_required
def scrape_user_products_view(request):
    try:
        # Get the current user's profile
        profile = Profile.objects.get(user=request.user)
        user_products = Product.objects.filter(profile=profile)

        # Extract product IDs to pass to the Celery tasks
        product_ids = list(user_products.values_list('id', flat=True))

        # Trigger the Celery tasks
        print('Scraping products for user...')
        scrape_user_products_task.delay(product_ids)
        
        print('Scraping bulk products for user...')
        scrape_user_Bulk_product_task.delay(product_ids)

        print('Caching data for user...')
        cache_user_data.delay(request.user.id)


        # Notify the user
        messages.success(request, "Updating the table is in progress. Please check back in a few minutes.")
    except Exception as e:
        print(f"Error in scrape_user_products_view: {e}")
        messages.error(request, "An error occurred during data scraping and caching. Please try again.")

    return redirect('dashboard:price')


@login_required
def dashboard_view(request):
    try:
        # Use caching
        cache_key = f'dashboard_data_{request.user.id}'
        cached_data = cache.get(cache_key)

        if not cached_data:
            return JsonResponse(
                {"error": "Am error occour please try again later, we are working on it."},
                status=400
            )

        # Pass cached data directly to Plotly Dash
        profile = Profile.objects.get(user=request.user)
        account_names = list(
            profile.products.values_list('accounts_id__name', flat=True).distinct().exclude(accounts_id__name__isnull=True)
        )
        plot_dashboard(cached_data, account_names)
        context = {
            'segment': 'dashboard_view',

        }
        return render(request, 'dashboard/dashboard.html', context)


    except Exception as e:
        print(f"Error in dashboard_view: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def performance_view(request):
    try:
        context = {
            'segment': 'scraped_data',
        }

        return render(request, 'dashboard/product_performance.html', context)

    except Exception as e:
        print(f"An error occurred in performance_view: {e}")
        return render(request, 'dashboard/product_performance.html', {
            'error_message': 'An error occurred while retrieving the data.'
        })


@login_required
def price(request):
    try:
        profile = Profile.objects.get(user=request.user)  # Assuming you have a user profile
        pinned_tables = profile.pinned_tables.all()


        # Get selected product IDs and selected columns from the request
        selected_product_ids = request.GET.getlist('products')
        selected_columns = request.GET.getlist('columns')

        # Filter products for the dropdown
        all_products = profile.products.all()
        filtered_products = all_products
        if selected_product_ids:
            filtered_products = filtered_products.filter(id__in=selected_product_ids)

        # Define dynamic columns based on user's accounts
        user_accounts = profile.products.values_list('accounts_id__name', flat=True).distinct().exclude(accounts_id__name__isnull=True)
        all_columns = []
        for account in user_accounts:
            account_lower = account.lower()
            all_columns.extend([
                {'name': f'{account_lower}_price', 'header': f'{account} Price'},
                {'name': f'{account_lower}_compliance_flag', 'header': f'{account} Compliance'},
                {'name': f'{account_lower}_discount', 'header': f'{account} Discount'},
            ])

        all_columns.extend([
                        {'name': 'promo_flag', 'header': 'Promo Flag'},
                        {'name': 'RSP', 'header': 'RSP'},
                        {'name': 'final_price', 'header': 'Reference Price'},
                        {'name': 'amazon_sold_by', 'header': 'Amazon KSA Sold By'},
                        {'name': 'noon_sa_sold_by', 'header': 'Noon KSA Sold By'},
                        {'name': 'opps', 'header': 'Online Price Performance Score'},
                        {'name': 'price_deviation_score', 'header': 'Price Deviation Score'},
                        {'name': 'account_deviation_score', 'header': 'Accunts Deviation Score'},
                    ])
        # Filter columns based on selected_columns
        if selected_columns:
            columns = [col for col in all_columns if col['name'] in selected_columns]
        else:
            # Default to show all columns if none selected
            columns = all_columns



        # Rest of your view logic continues here...
        # Subquery to find the maximum scraped_at date for each product
        max_date_subquery = ScrapedData.objects.filter(
            product=OuterRef('product')
        ).order_by('-scraped_at').values('scraped_at')[:1]

        # Get all scraped data where scraped_at is the max date for each product (fetch model instances)
        max_scraped_data = ScrapedData.objects.filter(
            scraped_at=Subquery(max_date_subquery),
            product__in=filtered_products
        ).select_related('product')

        # Get user accounts and filter out None values
        user_accounts = profile.products.values_list('accounts_id__name', flat=True).distinct().exclude(accounts_id__name__isnull=True)

        # Check if "amazon" is in the user's accounts
        show_amazon_sold_by = 'amazon' in user_accounts

        # Check if the current table is pinned by the user
        is_table_pinned = profile.pinned_tables.filter(table_name="CurrentPriceStatus").exists()

        # Find the maximum `scraped_at` date across all products
        latest_scraped_date = max_scraped_data.aggregate(latest_date=Max('scraped_at'))['latest_date']

        context = {
            'max_scraped_data': max_scraped_data,
            'latest_scraped_date': latest_scraped_date,
            'is_table_pinned': is_table_pinned,
            'segment': 'price',
            'user_accounts': user_accounts,
            'show_amazon_sold_by': show_amazon_sold_by,
            'columns': columns,
            'pinned_tables': pinned_tables,
            'selected_product_ids': selected_product_ids,
            'selected_columns': selected_columns,
            'all_products': all_products,  # Provide the list of all products
            'all_columns': all_columns,    # Provide the column data for the template
        }

        return render(request, 'dashboard/price.html', context)

    except Exception as e:
        print(f"An error occurred in price: {e}")
        return render(request, 'dashboard/price.html', {
            'error_message': 'An error occurred while retrieving the data.'
        })


@login_required
def download_performance_data(request):
    try:
        # Retrieve cached data
        cache_key = f'dashboard_data_{request.user.id}'
        cached_data = cache.get(cache_key)

        if not cached_data:
            return HttpResponse("Data is not yet cached. Please try again later.", status=400)

        # Deserialize cached data
        data = json.loads(cached_data)

        # Process data for Excel sheets
        scraped_data_df = pd.DataFrame([{
            'Scraped At': data['scraped_at'][i],
            'RSP VAT': data['RSP_VAT'][i],
            'Discount %': data['discount_percentage'][i],
            'Amazon Price': data['amazon_price'][i],
            'Nahdi Price': data['nahdi_price'][i],
            'Dawa Price': data['dawa_price'][i],
            'Noon_sa Price': data['noon_sa_price'][i],
            'Amazon Discount': data['amazon_discount'][i],
            'Nahdi Discount': data['nahdi_discount'][i],
            'Dawa Discount': data['dawa_discount'][i],
            'Noon_SA Discount': data['noon_sa_discount'][i],
            'Order Quantity': data['nahdi_ordered_qty'][i],
            'Brand': data['Brand'][i],
            'Category': data['Category'][i],
            'Subcategory': data['Subcategory'][i],
            'Product': data['Product'][i],
            'Account': data['Account'][i],
        } for i in range(len(data['scraped_at'])) if data['key_name'][i] is None])  # Filter `scraped_data`

        scraped_bulk_data_df = pd.DataFrame([{
            'Scraped At': data['scraped_at'][i],
            'Key Name': data['key_name'][i],
            'Amazon title': data['amazon_title'][i],
            'Amazon Price': data['amazon_price'][i],
            'Amazon Discount': data['amazon_discount'][i],
            'Nahdi title': data['nahdi_title'][i],
            'Nahdi Price': data['nahdi_price'][i],
            'Nahdi Discount': data['nahdi_discount'][i],
            'Dawa title': data['dawa_title'][i],
            'Dawa Price': data['dawa_price'][i],
            'Dawa Discount': data['dawa_discount'][i],
            'Noon_sa title': data['noon_sa_title'][i],
            'Noon_sa Price': data['noon_sa_price'][i],
            'Noon_SA Discount': data['noon_sa_discount'][i],
            'Order Quantity': data['nahdi_ordered_qty'][i],
        } for i in range(len(data['scraped_at'])) if data['key_name'][i] is not None])  # Filter `scraped_bulk_data`

        # Save DataFrames to an Excel file with two sheets
        with BytesIO() as b:
            with pd.ExcelWriter(b, engine='xlsxwriter') as writer:
                scraped_data_df.to_excel(writer, index=False, sheet_name='My Products')
                scraped_bulk_data_df.to_excel(writer, index=False, sheet_name='Bulk Search')
            b.seek(0)
            response = HttpResponse(
                b,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            response['Content-Disposition'] = 'attachment; filename="EcomMan.xlsx"'
            return response

    except Exception as e:
        print(f"Error in download_performance_data: {e}")
        return HttpResponse("An error occurred while generating the file.", status=500)


@login_required
def toggle_pin_table(request, table_name):
    profile = Profile.objects.get(user=request.user)
    pinned_table, created = PinnedTable.objects.get_or_create(table_name=table_name)
    if profile.pinned_tables.filter(table_name=table_name).exists():
        profile.pinned_tables.remove(pinned_table)
    else:
        profile.pinned_tables.add(pinned_table)

    return redirect(request.META.get('HTTP_REFERER', 'dashboard:price'))


@login_required
def index(request):
    try:
        profile = Profile.objects.get(user=request.user)  # Assuming you have a user profile
        pinned_tables = profile.pinned_tables.all()

        # Subquery to find the maximum scraped_at date for each product
        max_date_subquery = ScrapedData.objects.filter(
            product=OuterRef('product')
        ).order_by('-scraped_at').values('scraped_at')[:1]

        # Get all scraped data where scraped_at is the max date for each product (fetch model instances)
        max_scraped_data = ScrapedData.objects.filter(
        scraped_at=Subquery(max_date_subquery),
        product__profile=profile
    ).select_related('product')


        # # Get user accounts using accounts and urls
        # user_accounts = profile.products.values_list('accounts__name', flat=True).distinct()
        # Get user accounts and filter out None values
        user_accounts = profile.products.values_list('accounts_id__name', flat=True).distinct().exclude(accounts_id__name__isnull=True)
        # print('user_accounts', user_accounts)
        # Define all possible dynamic columns
        all_columns = [
            {'name': 'dawa_price', 'header': 'Dawa Price'},
            {'name': 'nahdi_price', 'header': 'Nahdi Price'},
            {'name': 'amazon_price', 'header': 'Amazon.SA Price'},
            {'name': 'noon_sa_price', 'header': 'Noon.SA Price'},
            {'name': 'dawa_compliance_flag', 'header': 'Dawa Compliance'},
            {'name': 'nahdi_compliance_flag', 'header': 'Nahdi Compliance'},
            {'name': 'amazon_compliance_flag', 'header': 'Amazon Compliance'},
            {'name': 'noon_sa_compliance_flag', 'header': 'Noon Compliance'},
        ]


        columns = [
            col for col in all_columns
            if col['name'] in [
                f"{account.lower()}_price" for account in user_accounts if account
            ] or col['name'] in [
                f"{account.lower()}_compliance_flag" for account in user_accounts if account
            ]
        ]
        # print(columns)


        # Check if "amazon" is in the user's accounts
        show_amazon_sold_by = 'amazon' in user_accounts

        # Check if the current table is pinned by the user
        is_table_pinned = profile.pinned_tables.filter(table_name="CurrentPriceStatus").exists()

        # Find the maximum `scraped_at` date across all products
        latest_scraped_date = max_scraped_data.aggregate(latest_date=Max('scraped_at'))['latest_date']




        # Retrieve cached data
        cache_key = f'dashboard_data_{request.user.id}'
        serialized_data = cache.get(cache_key)

        if serialized_data:
            # Deserialize if it's a JSON string
            if isinstance(serialized_data, str):
                try:
                    data = json.loads(serialized_data)
                    logger.info(f"Deserialized cached data: {data}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decoding failed: {e}")
                    data = None
            else:
                # Directly use data if not a string
                data = serialized_data
                logger.info(f"Using cached data directly: {data}")
        else:
            logger.warning(f"No cached data found for key {cache_key}")
            data = None

        # Check if data exists and process it without assumptions
        if data:
            logger.info(f"Processing cached data: {type(data)}")
            if isinstance(data, (list, dict)):
                scraped_data_df = pd.DataFrame(data)
                logger.info(f"DataFrame created: {scraped_data_df.head()}")

                # Example calculation: group by 'scraped_at' and calculate mean of 'opps'
                grouped_df = scraped_data_df.groupby('scraped_at').agg({'opps': 'mean'}).reset_index()
                latest_opps = grouped_df.iloc[0]['opps'] if not grouped_df.empty else None
                previous_opps = grouped_df.iloc[1]['opps'] if len(grouped_df) > 1 else None
                opps_difference = (
                    latest_opps - previous_opps if latest_opps is not None and previous_opps is not None else None
                )
                summary_data = {
                    'latest_opps': latest_opps,
                    'previous_opps': previous_opps,
                    'opps_difference': opps_difference,
                }
            else:
                # Handle unexpected data types
                logger.error(f"Unexpected data type: {type(data)}")
                summary_data = {'latest_opps': None, 'previous_opps': None, 'opps_difference': None}
        else:
            summary_data = {'latest_opps': None, 'previous_opps': None, 'opps_difference': None}

        context = {
            'summary_data': summary_data,
            'max_scraped_data': max_scraped_data,  # Now returning instances
            'latest_scraped_date': latest_scraped_date,
            'is_table_pinned': is_table_pinned,
            'segment': 'index',
            'user_accounts': user_accounts,
            'show_amazon_sold_by': show_amazon_sold_by,
            'columns': columns,
            'pinned_tables': pinned_tables,  # Pass the list of pinned tables
            'summary_data': summary_data,  # Summary for the latest and previous average opps
        }

        return render(request, 'dashboard/index.html', context)

    except Exception as e:
        # Log the exception or handle it as needed
        logger.error(f"Error in index view: {e}")
        return render(request, 'dashboard/index.html', {
          'error_message': 'An error occurred while retrieving the data.'
      })
