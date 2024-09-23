from django.shortcuts import render, redirect

from scrapper.models import ScrapedData
from client_profile.models import Profile, PromoPlan, PinnedTable #s,Product, Subcategory, Brand
from django.db.models import OuterRef, Subquery, Max, F, Value as V, FloatField
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Coalesce
from .dash_apps.app import plot_dashboard



@login_required
def dashboard_view(request):
    profile = Profile.objects.get(user=request.user)
    scraped_data = ScrapedData.objects.filter(product__profile=profile)

    # Prepare data in a format for Dash
    data = {
        'scraped_at': [item.scraped_at.isoformat() for item in scraped_data],
        'opps': [item.opps for item in scraped_data],
        'Category': [item.product.category for item in scraped_data],
        'Subcategory': [item.product.subcategory for item in scraped_data],
        'Product': [item.product.TITLE for item in scraped_data],
    }

    # Initialize the Dash app
    plot_dashboard(data)

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
        user_accounts = profile.products.values_list('accounts__name', flat=True).distinct()

        # Define all possible dynamic columns
        all_columns = [
            {'name': 'dawa_price', 'header': 'Dawa Price'},
            {'name': 'nahdi_price', 'header': 'Nahdi Price'},
            {'name': 'amazon_price', 'header': 'Amazon Price'},
            {'name': 'dawa_compliance_flag', 'header': 'Dawa Compliance'},
            {'name': 'nahdi_compliance_flag', 'header': 'Nahdi Compliance'},
            {'name': 'amazon_compliance_flag', 'header': 'Amazon Compliance'},
        ]

        # Filter columns to include only those related to user accounts (both price and compliance)
        columns = [
            col for col in all_columns
            if col['name'] in [
                f"{account.lower()}_price" for account in user_accounts
            ] or col['name'] in [
                f"{account.lower()}_compliance_flag" for account in user_accounts
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
        print(f"An error occurred: {e}")
        return render(request, 'dashboard/product_performance.html', {
            'error_message': 'An error occurred while retrieving the data.'
        })

import pandas as pd
# from django.db.models import Avg
# from django.db.models.functions import TruncDate

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


        # Get user accounts
        user_accounts = profile.products.values_list('accounts__name', flat=True).distinct()

        # Define all possible dynamic columns
        all_columns = [
            {'name': 'dawa_price', 'header': 'Dawa Price'},
            {'name': 'nahdi_price', 'header': 'Nahdi Price'},
            {'name': 'amazon_price', 'header': 'Amazon Price'},
            {'name': 'dawa_compliance_flag', 'header': 'Dawa Compliance'},
            {'name': 'nahdi_compliance_flag', 'header': 'Nahdi Compliance'},
            {'name': 'amazon_compliance_flag', 'header': 'Amazon Compliance'},
        ]

        # Filter columns to include only those related to user accounts (both price and compliance)
        columns = [
            col for col in all_columns
            if col['name'] in [
                f"{account.lower()}_price" for account in user_accounts
            ] or col['name'] in [
                f"{account.lower()}_compliance_flag" for account in user_accounts
            ]
        ]

        # Check if "amazon" is in the user's accounts
        show_amazon_sold_by = 'amazon' in user_accounts

        # Check if the current table is pinned by the user
        is_table_pinned = profile.pinned_tables.filter(table_name="CurrentPriceStatus").exists()

        # Find the maximum `scraped_at` date across all products
        latest_scraped_date = max_scraped_data.aggregate(latest_date=Max('scraped_at'))['latest_date']


        # plot
        scraped_data = ScrapedData.objects.filter(product__profile=profile)
        # Prepare data in a format for Dash
        data = {
            'scraped_at': [item.scraped_at.isoformat() for item in scraped_data],
            'opps': [item.opps for item in scraped_data],
            'Category': [item.product.category for item in scraped_data],
            'Subcategory': [item.product.subcategory for item in scraped_data],
            'Product': [item.product.TITLE for item in scraped_data],
        }

        # Initialize the Dash app
        plot_dashboard(data)

        context = {
            'scraped_data': scraped_data,
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
        print(f"An error occurred: {e}")
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





# """Old price function working"""
# @login_required
# def price(request):
#     try:
#         profile = Profile.objects.get(user=request.user)

#         # Subquery to find the maximum scraped_at date for each product
#         max_date_subquery = ScrapedData.objects.filter(
#             product=OuterRef('product')
#         ).order_by('-scraped_at').values('scraped_at')[:1]

#         # Get all scraped data where scraped_at is the max date for each product
#         max_scraped_data = ScrapedData.objects.filter(
#             scraped_at=Subquery(max_date_subquery),
#             product__profile=profile
#         ).values(
#             'product_id', 'product__TITLE', 'product__RSP', 'product__RSP_VAT',
#             'scraped_at', 'amazon_sold_by'
#         ).annotate(
#             dawa_price=Coalesce(F('dawa_price'), V(0), output_field=FloatField()),
#             nahdi_price=Coalesce(F('nahdi_price'), V(0), output_field=FloatField()),
#             amazon_price=Coalesce(F('amazon_price'), V(0), output_field=FloatField())
#         )

#         # Get Promo Plans for the profile
#         promo_plans = PromoPlan.objects.filter(profile=profile).select_related('product')

#         # Convert Promo Plans to a dictionary for easy access
#         promo_plan_dict = {plan.product.id: plan for plan in promo_plans}

#         # Combine Scraped Data with Promo Plan Data
#         for data in max_scraped_data:
#             product_id = data['product_id']
#             promo_plan = promo_plan_dict.get(product_id)
#             if promo_plan and promo_plan.is_on_sale:
#                 data['on_promo'] = True
#                 data['my_price'] = promo_plan.desired_price
#             else:
#                 data['on_promo'] = False
#                 data['my_price'] = data['product__RSP_VAT']

#         # Dynamic columns for the prices based on the user's accounts
#         user_accounts = profile.products.values_list('accounts__name', flat=True).distinct()

#         # Check if "amazon" is in the user's accounts
#         show_amazon_sold_by = 'amazon' in user_accounts

#         # Find the maximum `scraped_at` date across all products
#         latest_scraped_date = max_scraped_data.aggregate(latest_date=Max('scraped_at'))['latest_date']

#         # Check if the current table is pinned by the user
#         is_table_pinned = profile.pinned_tables.filter(table_name="CurrentPriceTable").exists()

#         context = {
#             'max_scraped_data': max_scraped_data,
#             'latest_scraped_date': latest_scraped_date,
#             'is_table_pinned': is_table_pinned,
#             'segment': 'price',
#             'user_accounts': user_accounts,  # Pass the dynamic account list to the template
#             'show_amazon_sold_by': show_amazon_sold_by,  # Pass the boolean to the template
#         }

#         return render(request, 'dashboard/price.html', context)

#     except Exception as e:
#         # Log the exception or handle it as needed
#         print(f"An error occurred: {e}")
#         return render(request, 'dashboard/price.html', {
#             'error_message': 'An error occurred while retrieving the data.'
#         })
# newer version
# def price(request):
#     try:
#         profile = Profile.objects.get(user=request.user)  # Assuming you have a user profile
#         pinned_tables = profile.pinned_tables.all()

#         # Subquery to find the maximum scraped_at date for each product
#         max_date_subquery = ScrapedData.objects.filter(
#             product=OuterRef('product')
#         ).order_by('-scraped_at').values('scraped_at')[:1]

#         # Get all scraped data where scraped_at is the max date for each product (fetch model instances)
#         max_scraped_data = ScrapedData.objects.filter(
#         scraped_at=Subquery(max_date_subquery),
#         product__profile=profile
#     ).select_related('product')


#         # Get user accounts
#         user_accounts = profile.products.values_list('accounts__name', flat=True).distinct()

#         # Define all possible dynamic columns
#         all_columns = [
#             {'name': 'dawa_price', 'header': 'Dawa Price'},
#             {'name': 'nahdi_price', 'header': 'Nahdi Price'},
#             {'name': 'amazon_price', 'header': 'Amazon Price'},
#             {'name': 'dawa_compliance_flag', 'header': 'Dawa Compliance'},
#             {'name': 'nahdi_compliance_flag', 'header': 'Nahdi Compliance'},
#             {'name': 'amazon_compliance_flag', 'header': 'Amazon Compliance'},
#         ]

#         # Filter columns to include only those related to user accounts (both price and compliance)
#         columns = [
#             col for col in all_columns
#             if col['name'] in [
#                 f"{account.lower()}_price" for account in user_accounts
#             ] or col['name'] in [
#                 f"{account.lower()}_compliance_flag" for account in user_accounts
#             ]
#         ]

#         # Check if "amazon" is in the user's accounts
#         show_amazon_sold_by = 'amazon' in user_accounts

#         # Check if the current table is pinned by the user
#         is_table_pinned = profile.pinned_tables.filter(table_name="CurrentPriceStatus").exists()

#         # Find the maximum `scraped_at` date across all products
#         latest_scraped_date = max_scraped_data.aggregate(latest_date=Max('scraped_at'))['latest_date']


        # # plot
        # scraped_data = ScrapedData.objects.filter(product__profile=profile)
        # # Prepare data in a format for Dash
        # data = {
        #     'scraped_at': [item.scraped_at.isoformat() for item in scraped_data],
        #     'opps': [item.opps for item in scraped_data],
        #     'Category': [item.product.category for item in scraped_data],
        #     'Subcategory': [item.product.subcategory for item in scraped_data],
        #     'Product': [item.product.TITLE for item in scraped_data],
        # }

        # # Initialize the Dash app
        # plot_dashboard(data)

#         context = {
#             'scraped_data': scraped_data,
#             'max_scraped_data': max_scraped_data,  # Now returning instances
#             'latest_scraped_date': latest_scraped_date,
#             'is_table_pinned': is_table_pinned,
#             'segment': 'price',
#             'user_accounts': user_accounts,
#             'show_amazon_sold_by': show_amazon_sold_by,
#             'columns': columns,
#             'pinned_tables': pinned_tables,  # Pass the list of pinned tables
#         }

#         return render(request, 'dashboard/price.html', context)

#     except Exception as e:
#         # Log the exception or handle it as needed
#         print(f"An error occurred: {e}")
#         return render(request, 'dashboard/price.html', {
#             'error_message': 'An error occurred while retrieving the data.'
#         })


# @login_required
# def curent_price_view(request):
#     try:
#         profile = Profile.objects.get(user=request.user)

#         # Fetch all scraped data for the products associated with the logged-in user's profile
#         scraped_data = ScrapedData.objects.filter(
#             product__profile=profile
#         )

#         # Get user accounts
#         user_accounts = profile.products.values_list('accounts__name', flat=True).distinct()

#         # Define all possible dynamic columns
#         all_columns = [
#             {'name': 'dawa_price', 'header': 'Dawa Price'},
#             {'name': 'nahdi_price', 'header': 'Nahdi Price'},
#             {'name': 'amazon_price', 'header': 'Amazon Price'},
#             {'name': 'dawa_compliance_flag', 'header': 'Dawa Compliance'},
#             {'name': 'nahdi_compliance_flag', 'header': 'Nahdi Compliance'},
#             {'name': 'amazon_compliance_flag', 'header': 'Amazon Compliance'},
#         ]

#         # Filter columns to include only those related to user accounts (both price and compliance)
#         columns = [
#             col for col in all_columns
#             if col['name'] in [
#                 f"{account.lower()}_price" for account in user_accounts
#             ] or col['name'] in [
#                 f"{account.lower()}_compliance_flag" for account in user_accounts
#             ]
#         ]

#         # Check if "amazon" is in the user's accounts
#         show_amazon_sold_by = 'amazon' in user_accounts


#         # Prepare the context with additional fields like OPPS, PCS, and product title
#         context = {
#             'scraped_data': scraped_data,
#             'columns': columns,
#             'show_amazon_sold_by': show_amazon_sold_by,  # Pass the boolean to the template

#         }

#         return render(request, 'dashboard/product_performance2.html', context)

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return render(request, 'dashboard/product_performance2.html', {
#             'error_message': 'An error occurred while retrieving the data.'
#         })

# @login_required
# def performance_view(request):
#     profile = Profile.objects.get(user=request.user)

#     # scraped_data = ScrapedData.objects.all()
#     scraped_data = ScrapedData.objects.filter(product__profile=profile)
#     context = {
#         'scraped_data': scraped_data,
#     }
#     return render(request, 'dashboard/performance.html', context)


# @login_required
# def product_performance_view(request):
#     try:
#         profile = Profile.objects.get(user=request.user)

#         # Fetch all scraped data for the products associated with the logged-in user's profile
#         scraped_data = ScrapedData.objects.filter(
#             product__profile=profile
#         ).values(
#             'product_id', 'product__TITLE', 'product__RSP', 'product__RSP_VAT',
#             'scraped_at', 'amazon_sold_by',
#         ).annotate(
#             dawa_price=Coalesce(F('dawa_price'), V(0), output_field=FloatField()),
#             nahdi_price=Coalesce(F('nahdi_price'), V(0), output_field=FloatField()),
#             amazon_price=Coalesce(F('amazon_price'), V(0), output_field=FloatField())
#         )

#         # Fetch Promo Plans for the profile
#         promo_plans = PromoPlan.objects.filter(profile=profile).select_related('product')

#         # Convert Promo Plans to a dictionary for easy access
#         promo_plan_dict = {plan.product.id: plan for plan in promo_plans}

#         # Get user accounts
#         user_accounts = profile.products.values_list('accounts__name', flat=True).distinct()

#         # Define the column names and headers dynamically based on user accounts
#         all_columns = [
#             {'name': 'dawa_price', 'header': 'Dawa Price'},
#             {'name': 'nahdi_price', 'header': 'Nahdi Price'},
#             {'name': 'amazon_price', 'header': 'Amazon Price'},
#         ]

#         # Filter columns to include only those related to user accounts
#         columns = [col for col in all_columns if col['name'] in [f"{account.lower()}_price" for account in user_accounts]]

#         performance_data = []

#         for data in scraped_data:
#             product_id = data['product_id']
#             promo_plan = promo_plan_dict.get(product_id)
#             if promo_plan and promo_plan.is_on_sale:
#                 desired_price = promo_plan.desired_price
#                 on_promo = True
#             else:
#                 desired_price = data['product__RSP_VAT']
#                 on_promo = False

#             # Initialize store prices and compliance flags
#             store_prices = []
#             compliance_flags = {}

#             # Dynamically access the price fields
#             for account in user_accounts:
#                 price_field = f"{account.lower()}_price"
#                 price = data.get(price_field, 0)
#                 store_prices.append(price)
#                 compliance_flags[account] = abs(price - desired_price) > 10

#             # Calculate PDS, PCS, and OPPS
#             pds = calculate_pds(desired_price, store_prices)
#             pcs_calculated = round(calculate_pcs(desired_price, store_prices), 2)
#             opps = round((pcs_calculated + pds) / 2, 2)

#             # Prepare the row data based on filtered columns
#             row_data = {
#                 'product': data['product__TITLE'],
#                 'pds': pds,
#                 'pcs': pcs_calculated,
#                 'opps': opps,
#                 'scraped_at': data['scraped_at'],
#                 'amazon_sold_by': data['amazon_sold_by'],
#                 'compliance_flags': compliance_flags,
#                 'user_accounts': user_accounts,
#                 'on_promo': on_promo,
#                 'my_price': desired_price
#             }

#             # Add only the relevant prices to the row data
#             for col in columns:
#                 row_data[col['name']] = data.get(col['name'], 0)

#             performance_data.append(row_data)

#         context = {
#             'performance_data': performance_data,
#             'columns': columns,
#             'user_accounts': user_accounts,  # Ensure this is included
#             'segment': 'performance',
#         }

#         return render(request, 'dashboard/product_performance.html', context)

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return render(request, 'dashboard/product_performance.html', {
#             'error_message': 'An error occurred while retrieving the data.'
#         })

# @login_required
# def price(request):
#     try:
#         profile = Profile.objects.get(user=request.user)

#         # Subquery to find the maximum scraped_at date for each product
#         max_date_subquery = ScrapedData.objects.filter(
#             product=OuterRef('product')
#         ).order_by('-scraped_at').values('scraped_at')[:1]

#         # # Get all scraped data where scraped_at is the max date for each product
#         # max_scraped_data = ScrapedData.objects.filter(
#         #     scraped_at=Subquery(max_date_subquery),
#         #     product__profile=profile
#         # ).values(
#         #     'product_id', 'product__TITLE', 'product__RSP', 'product__RSP_VAT',
#         #     'scraped_at', 'amazon_sold_by', 'dawa_price', 'nahdi_price', 'amazon_price')


#         # Get all scraped data where scraped_at is the max date for each product
#         max_scraped_data = ScrapedData.objects.filter(
#                     scraped_at=Subquery(max_date_subquery),
#                     product__profile=profile
#                 )

#         # Get user accounts
#         user_accounts = profile.products.values_list('accounts__name', flat=True).distinct()

#         # Define all possible dynamic columns
#         all_columns = [
#             {'name': 'dawa_price', 'header': 'Dawa Price'},
#             {'name': 'nahdi_price', 'header': 'Nahdi Price'},
#             {'name': 'amazon_price', 'header': 'Amazon Price'},
#             {'name': 'dawa_compliance_flag', 'header': 'Dawa Compliance'},
#             {'name': 'nahdi_compliance_flag', 'header': 'Nahdi Compliance'},
#             {'name': 'amazon_compliance_flag', 'header': 'Amazon Compliance'},
#         ]

#         # Filter columns to include only those related to user accounts (both price and compliance)
#         columns = [
#             col for col in all_columns
#             if col['name'] in [
#                 f"{account.lower()}_price" for account in user_accounts
#             ] or col['name'] in [
#                 f"{account.lower()}_compliance_flag" for account in user_accounts
#             ]
#         ]

#         # Check if "amazon" is in the user's accounts
#         show_amazon_sold_by = 'amazon' in user_accounts

#         # Check if the current table is pinned by the user
#         is_table_pinned = profile.pinned_tables.filter(table_name="CurrentPrice").exists()        
#         # Prepare the context with additional fields like OPPS, PCS, and product title

#         # Find the maximum `scraped_at` date across all products
#         latest_scraped_date = max_scraped_data.aggregate(latest_date=Max('scraped_at'))['latest_date']


#         context = {
#             'max_scraped_data': max_scraped_data,
#             'latest_scraped_date': latest_scraped_date,
#             'is_table_pinned': is_table_pinned,
#             'segment': 'price',
#             'user_accounts': user_accounts,  # Pass the dynamic account list to the template
#             'show_amazon_sold_by': show_amazon_sold_by,  # Pass the boolean to the template
#             'columns': columns,
#         }

#         return render(request, 'dashboard/price copy.html', context)

#     except Exception as e:
#         # Log the exception or handle it as needed
#         print(f"An error occurred: {e}")
#         return render(request, 'dashboard/price copy.html', {
#             'error_message': 'An error occurred while retrieving the data.'
#         })
# def price(request):
#     profile = request.user.profile  # Assuming you have a user profile
    
#     # Subquery to get the max scraped_at for each product
#     max_date_subquery = ScrapedData.objects.filter(
#         product=OuterRef('product')
#     ).order_by('-scraped_at').values('scraped_at')[:1]
    
#     # Main query to get the filtered data
#     scraped_data = ScrapedData.objects.filter(
#         scraped_at=Subquery(max_date_subquery),
#         product__profile=profile
#     )

#     # Pass the full queryset (without .values()) to the template
#     context = {
#         'scraped_data': scraped_data,
#     }
#     return render(request, 'dashboard/price copy.html', context)

# def combined_view(request):
#     return render(request, 'dashboard/combined_view.html')
