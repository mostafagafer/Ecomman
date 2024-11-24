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
from django.contrib import messages

@login_required
def scrape_user_products_view(request):
    # Get the current user's profile
    profile = Profile.objects.get(user=request.user)
    print("Profile:", profile)
    
    # Get only the products associated with the user's profile
    user_products = Product.objects.filter(profile=profile)
    print("user_products:", user_products)

    # Extract product IDs to pass to the Celery task
    product_ids = list(user_products.values_list('id', flat=True))
    # print("product_ids:", user_products)

    # Trigger the Celery task, passing the product IDs
    print('scraping products for user')
    scrape_user_products_task.delay(product_ids)
    
    print('scraping bulk products for user')
    scrape_user_Bulk_product_task.delay(product_ids)
    messages.success(request, "Updating the table is in progress. Please check back in a few moments.")

    # Redirect to a page or render a template
    return redirect('dashboard:price')

def dashboard_view(request):
    profile = Profile.objects.get(user=request.user)
    scraped_data = ScrapedData.objects.filter(product__profile=profile)

    # Get unique accounts associated with the user
    user_accounts = list(profile.products.values_list('accounts_id__name', flat=True).distinct().exclude(accounts_id__name__isnull=True))

    # Get categories and subcategories for the products
    categories = profile.products.values_list('category__name', flat=True).distinct()
    subcategories = profile.products.values_list('subcategory__name', flat=True).distinct()
    
    # Combine categories and subcategories into a single list of key names
    key_names = list(categories) + list(subcategories)

    # Filter ScrapedBulkData based on key_name matching category or subcategory
    scraped_bulk_data = ScrapedBulkData.objects.filter(key_name__in=key_names)

    # Prepare data dictionary
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

    # Populate data from scraped_data
    for item in scraped_data:
        data['scraped_at'].append(item.scraped_at.isoformat())
        data['RSP_VAT'].append(item.product.RSP_VAT)
        data['discount_percentage'].append(item.discount_percentage if item.discount_percentage is not None else None)
        data['key_name'].append(None)  # Placeholder for bulk-only field
        data['amazon_title'].append(item.amazon_title if item.amazon_title is not None else None)
        data['dawa_title'].append(item.dawa_title if item.dawa_title is not None else None)
        data['nahdi_title'].append(item.nahdi_title if item.nahdi_title is not None else None)
        data['noon_sa_title'].append(item.noon_sa_title if item.noon_sa_title is not None else None)
        data['amazon_price'].append(item.amazon_price if item.amazon_price is not None else None)
        data['dawa_price'].append(item.dawa_price if item.dawa_price is not None else None)
        data['nahdi_price'].append(item.nahdi_price if item.nahdi_price is not None else None)
        data['amazon_discount'].append(item.amazon_discount if item.amazon_discount is not None else None)
        data['dawa_discount'].append(item.dawa_discount if item.dawa_discount is not None else None)
        data['nahdi_discount'].append(item.nahdi_discount if item.nahdi_discount is not None else None)
        data['nahdi_ordered_qty'].append(item.nahdi_ordered_qty if item.nahdi_ordered_qty is not None else None)
        data['noon_sa_price'].append(item.noon_sa_price if item.noon_sa_price is not None else None)
        data['noon_sa_discount'].append(item.noon_sa_discount if item.noon_sa_discount is not None else None)
        data['opps'].append(item.opps)
        data['Brand'].append(item.product.brand)
        data['Category'].append(item.product.category)
        data['Subcategory'].append(item.product.subcategory)
        data['Product'].append(item.product.TITLE)

        # Account concatenation
        accounts = item.product.accounts_id.all()
        account_names = [account.name for account in accounts]
        data['Account'].append(", ".join(account_names) if account_names else None)

    # Populate data from scraped_bulk_data
    for bulk_item in scraped_bulk_data:
        data['scraped_at'].append(bulk_item.scraped_at.isoformat())
        data['RSP_VAT'].append(None)  # Placeholder for non-bulk field
        data['discount_percentage'].append(None)  # Placeholder for non-bulk field
        data['key_name'].append(bulk_item.key_name)
        data['amazon_title'].append(bulk_item.amazon_title if bulk_item.amazon_title is not None else None)
        data['dawa_title'].append(bulk_item.dawa_title if bulk_item.dawa_title is not None else None)
        data['nahdi_title'].append(bulk_item.nahdi_title if bulk_item.nahdi_title is not None else None)
        data['noon_sa_title'].append(bulk_item.noon_sa_title if bulk_item.noon_sa_title is not None else None)
        data['amazon_price'].append(bulk_item.amazon_price if bulk_item.amazon_price is not None else None)
        data['dawa_price'].append(bulk_item.dawa_price if bulk_item.dawa_price is not None else None)
        data['nahdi_price'].append(bulk_item.nahdi_price if bulk_item.nahdi_price is not None else None)
        data['amazon_discount'].append(bulk_item.amazon_discount if bulk_item.amazon_discount is not None else None)
        data['dawa_discount'].append(bulk_item.dawa_discount if bulk_item.dawa_discount is not None else None)
        data['nahdi_discount'].append(bulk_item.nahdi_discount if bulk_item.nahdi_discount is not None else None)
        data['nahdi_ordered_qty'].append(bulk_item.nahdi_ordered_qty if bulk_item.nahdi_ordered_qty is not None else None)

        data['noon_sa_price'].append(bulk_item.noon_sa_price if bulk_item.noon_sa_price is not None else None)
        data['noon_sa_discount'].append(bulk_item.noon_sa_discount if bulk_item.noon_sa_discount is not None else None)

        data['opps'].append(None)  # Placeholder for non-bulk field
        data['Brand'].append(None)  # Placeholder for non-bulk field
        data['Category'].append(None)  # Placeholder for non-bulk field
        data['Subcategory'].append(None)  # Placeholder for non-bulk field
        data['Product'].append(None)  # Placeholder for non-bulk field
        data['Account'].append(None)  # Placeholder for non-bulk field



    # Initialize the Dash app
    plot_dashboard(data, user_accounts)

    context = {}
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def performance_view(request):
    try:
        profile = Profile.objects.get(user=request.user)

        # Fetch all scraped data for the products associated with the logged-in user's profile
        scraped_data = ScrapedData.objects.filter(
            product__profile=profile
        )

        # Get user accounts
        user_accounts = profile.products.values_list('accounts_id__name', flat=True).distinct().exclude(accounts_id__name__isnull=True)

        # Define all possible dynamic columns
        all_columns = [
            {'name': 'dawa_price', 'header': 'Dawa Price'},
            {'name': 'nahdi_price', 'header': 'Nahdi Price'},
            {'name': 'amazon_price', 'header': 'Amazon.SA Price'},
            {'name': 'dawa_compliance_flag', 'header': 'Dawa Compliance'},
            {'name': 'nahdi_compliance_flag', 'header': 'Nahdi Compliance'},
            {'name': 'amazon_compliance_flag', 'header': 'Amazon Compliance'},
        ]

        columns = [
            col for col in all_columns
            if col['name'] in [
                f"{account.lower()}_price" for account in user_accounts if account
            ] or col['name'] in [
                f"{account.lower()}_compliance_flag" for account in user_accounts if account
            ]
        ]

        # Check if "amazon" is in the user's accounts
        show_amazon_sold_by = 'amazon' in user_accounts

        # Check if the current table is pinned by the user
        is_table_pinned = profile.pinned_tables.filter(table_name="PerformanceData").exists()        
        # Prepare the context with additional fields like OPPS, PCS, and product title
        context = {
            'scraped_data': scraped_data,
            'columns': columns,
            'show_amazon_sold_by': show_amazon_sold_by,  # Pass the boolean to the template
            'is_table_pinned': is_table_pinned,
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
        print('user_accounts', user_accounts)
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
        print(columns)


        # Check if "amazon" is in the user's accounts
        show_amazon_sold_by = 'amazon' in user_accounts

        # Check if the current table is pinned by the user
        is_table_pinned = profile.pinned_tables.filter(table_name="CurrentPriceStatus").exists()

        # Find the maximum `scraped_at` date across all products
        latest_scraped_date = max_scraped_data.aggregate(latest_date=Max('scraped_at'))['latest_date']


        # # plot
        # scraped_data = ScrapedData.objects.filter(product__profile=profile)
        # # Prepare data in a format for Dash
        # data = {
        #     'scraped_at': [item.scraped_at.isoformat() for item in scraped_data],
        #     'opps': [item.opps for item in scraped_data],
        #     'Category': [item.product.category for item in scraped_data],
        #     'Subcategory': [item.product.subcategory for item in scraped_data],
        #     'Product': [item.product.TITLE for item in scraped_data],
        #     'amazon_price': [item.amazon_price for item in scraped_data],
        #     'nahdi_price': [item.nahdi_price for item in scraped_data],
        #     'dawa_price': [item.dawa_price for item in scraped_data],

        # }

        # # Initialize the Dash app
        # plot_dashboard(data)

        context = {
            # 'scraped_data': scraped_data,
            'max_scraped_data': max_scraped_data,  # Now returning instances
            'latest_scraped_date': latest_scraped_date,
            'is_table_pinned': is_table_pinned,
            'segment': 'price',
            'user_accounts': user_accounts,
            'show_amazon_sold_by': show_amazon_sold_by,
            'columns': columns,
            'pinned_tables': pinned_tables,  # Pass the list of pinned tables
        }

        return render(request, 'dashboard/price.html', context)

    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred in price: {e}")
        return render(request, 'dashboard/price.html', {
            'error_message': 'An error occurred while retrieving the data.'
        })



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


    #   # Get user accounts
    #   user_accounts = profile.products.values_list('accounts__name', flat=True).distinct()

    #   # Define all possible dynamic columns
    #   all_columns = [
    #       {'name': 'dawa_price', 'header': 'Dawa Price'},
    #       {'name': 'nahdi_price', 'header': 'Nahdi Price'},
    #       {'name': 'amazon_price', 'header': 'Amazon Price'},
    #       {'name': 'dawa_compliance_flag', 'header': 'Dawa Compliance'},
    #       {'name': 'nahdi_compliance_flag', 'header': 'Nahdi Compliance'},
    #       {'name': 'amazon_compliance_flag', 'header': 'Amazon Compliance'},
    #   ]

    #   # Filter columns to include only those related to user accounts (both price and compliance)
    #   columns = [
    #     col for col in all_columns
    #     if col['name'] in [
    #         f"{account.lower()}_price" for account in user_accounts
    #     ] or col['name'] in [
    #         f"{account.lower()}_compliance_flag" for account in user_accounts
    #     ]
    # ]
    # Get user accounts
      user_accounts = profile.products.values_list('accounts_id__name', flat=True).distinct().exclude(accounts_id__name__isnull=True)

        # Define all possible dynamic columns
      all_columns = [
            {'name': 'dawa_price', 'header': 'Dawa Price'},
            {'name': 'nahdi_price', 'header': 'Nahdi Price'},
            {'name': 'amazon_price', 'header': 'Amazon.SA Price'},
            {'name': 'dawa_compliance_flag', 'header': 'Dawa Compliance'},
            {'name': 'nahdi_compliance_flag', 'header': 'Nahdi Compliance'},
            {'name': 'amazon_compliance_flag', 'header': 'Amazon Compliance'},
        ]

      columns = [
            col for col in all_columns
            if col['name'] in [
                f"{account.lower()}_price" for account in user_accounts if account
            ] or col['name'] in [
                f"{account.lower()}_compliance_flag" for account in user_accounts if account
            ]
        ]


      # Check if "amazon" is in the user's accounts
      show_amazon_sold_by = 'amazon' in user_accounts

      # Check if the current table is pinned by the user
      is_table_pinned = profile.pinned_tables.filter(table_name="CurrentPriceStatus").exists()

      # Find the maximum `scraped_at` date across all products
      latest_scraped_date = max_scraped_data.aggregate(latest_date=Max('scraped_at'))['latest_date']




      # Filter max scraped data for each product
      scraped_data = ScrapedData.objects.filter(
          product__profile=profile
      ).select_related('product')

      # Step 1: Convert scraped_at to date (ignore time) and create a list for dataframe
      scraped_data_list = []
      for data in scraped_data:
          scraped_data_list.append({
              'scraped_at': data.scraped_at.strftime('%Y-%m-%d'),  # Convert to date string format
              'opps': data.opps  # Use cached_property opps here
          })

      scraped_data_df = pd.DataFrame(scraped_data_list)

      # Step 2: Group by scraped_at (ignoring the product) and calculate the average opps per day
      grouped_df = scraped_data_df.groupby('scraped_at').agg({'opps': 'mean'}).reset_index()

      # Step 3: Sort by scraped_at to get the latest and second-latest average opps
      grouped_df = grouped_df.sort_values(by='scraped_at', ascending=False)

      # Step 4: Get the latest and previous average opps
      latest_opps = grouped_df.iloc[0]['opps'] if not grouped_df.empty else None
      previous_opps = grouped_df.iloc[1]['opps'] if len(grouped_df) > 1 else None

      # Step 5: Calculate the difference between the latest and previous opps
      opps_difference = latest_opps - previous_opps if latest_opps is not None and previous_opps is not None else None

      # Prepare data for template rendering
      summary_data = {
          'latest_opps': latest_opps,
          'previous_opps': previous_opps,
          'opps_difference': opps_difference,
      }

      context = {
          'scraped_data': scraped_data,
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
      print(f"An error occurred in index: {e}")
      return render(request, 'dashboard/index.html', {
          'error_message': 'An error occurred while retrieving the data.'
      })

# @login_required
# def price_view(request):
#     return render(request, 'dashboard/price_view.html')

