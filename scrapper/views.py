from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from scrapper.models import  ScrapedData
from client_profile.models import Profile, PinnedTable
from django.shortcuts import get_object_or_404, redirect


# @login_required
# def user_scraped_data(request):
#     profile = Profile.objects.get(user=request.user)
#     scraped_data = ScrapedData.objects.filter(product__profile=profile)

#     # Check if the current table is pinned by the user
#     is_table_pinned = profile.pinned_tables.filter(table_name="ScrapedDataTable").exists()
#     return render(request, 'scrapper/user_scraped_data.html', {
#         'scraped_data': scraped_data,
#         'is_table_pinned': is_table_pinned,
#         'segment': 'scraped_data',
#     })



# @login_required
# def user_scraped_data(request):
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

#         # Check if the current table is pinned by the user
#         is_table_pinned = profile.pinned_tables.filter(table_name="ScrapedDataTable").exists()        
#         # Prepare the context with additional fields like OPPS, PCS, and product title
#         context = {
#             'scraped_data': scraped_data,
#             'columns': columns,
#             'show_amazon_sold_by': show_amazon_sold_by,  # Pass the boolean to the template
#             'is_table_pinned': is_table_pinned,
#             'segment': 'scraped_data',
#         }

#         return render(request, 'scrapper/user_scraped_data.html', context)

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return render(request, 'scrapper/user_scraped_data.html', {
#             'error_message': 'An error occurred while retrieving the data.'
#         })

# @login_required
# def toggle_pin_table(request, table_name):
#     profile = Profile.objects.get(user=request.user)
    
#     pinned_table, created = PinnedTable.objects.get_or_create(table_name=table_name)
#     if profile.pinned_tables.filter(table_name=table_name).exists():
#         profile.pinned_tables.remove(pinned_table)
#     else:
#         profile.pinned_tables.add(pinned_table)
    
#     return redirect('scrapper:user_scraped_data')

# def test_view(request):
#     test_data = ScrapedData.objects.all()
#     return render(request, 'scrapper/test.html', {'test_data': test_data})



# @login_required
# def pinned_tables_view(request):
#     pinned_tables = PinnedTable.objects.filter(user=request.user)
#     return render(request, 'scrapper/pinned_tables.html', {'pinned_tables': pinned_tables})

# @login_required
# def toggle_pin_table(request, table_id):
#     table = get_object_or_404(ScrapedData, id=table_id)
#     if request.user in table.pinned_by.all():
#         table.pinned_by.remove(request.user)
#     else:
#         table.pinned_by.add(request.user)
#     return redirect('scrapper:scraped_data')  # Adjust the redirect URL as necessary
# import time
# from .tasks import send_mass_emails, TheFunc


# # Create your views here.
# def send_campaign_email(request):
#     TheFunc.delay()
#     return render(request, 'campaign.html', {})

# def product_list(request):
#     products = Product.objects.all()
#     return render(request, 'scrapper/product_list.html', {'products': products})


# def scraped_data_list(request):
#     scraped_data = ScrapedData.objects.all()
#     # Order by scraped_at in descending order
#     # scraped_data = ScrapedData.objects.select_related('product').order_by('-scraped_at')
#     return render(request, 'scrapper/scraped_data_list.html', {'scraped_data': scraped_data})
