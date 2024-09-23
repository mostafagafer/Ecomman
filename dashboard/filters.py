# import django_filters
# from client_profile.models import Product
# from django import forms
# from django.utils import timezone

# dashboard/filters.py
import django_filters
# from .models import PerformanceData

import django_filters
from django import forms
from .models import PerformanceData
from django.utils import timezone
from datetime import timedelta


# filter.py
from django import forms
from client_profile.models import Product 

DATE_RANGE_CHOICES = [
    ('1d', 'Last 1 Day'),
    ('1w', 'Last 1 Week'),
    ('1m', 'Last 1 Month'),
    ('3m', 'Last 3 Months'),
    ('6m', 'Last 6 Months'),
    ('1y', 'Last 1 Year'),
]

class DateRangeFilterForm(forms.Form):
    date_range = forms.ChoiceField(choices=DATE_RANGE_CHOICES, required=True)
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False)

    def filter_performance_data(self, queryset):
        date_range = self.cleaned_data['date_range']
        product = self.cleaned_data['product']
        now = timezone.now()

        if date_range == '1d':
            start_date = now - timedelta(days=1)
        elif date_range == '1w':
            start_date = now - timedelta(weeks=1)
        elif date_range == '1m':
            start_date = now - timedelta(days=30)
        elif date_range == '3m':
            start_date = now - timedelta(days=90)
        elif date_range == '6m':
            start_date = now - timedelta(days=180)
        elif date_range == '1y':
            start_date = now - timedelta(days=365)

        queryset = queryset.filter(scraped_at__gte=start_date)
        if product:
            queryset = queryset.filter(product=product)

        return queryset

# class ScrapedDataFilter(django_filters.FilterSet):
#     class Meta:
#         model = ScrapedData
#         fields = {
#             'product__TITLE': ['icontains'],
#             'dawa_price': ['gte', 'lte'],
#             'nahdi_price': ['gte', 'lte'],
#             'amazon_price': ['gte', 'lte'],
#             'scraped_at': ['gte', 'lte'],
#         }

# from django import template

# register = template.Library()

# @register.filter
# def get_price_for_account(scraped_data, account):
#     account_price_field = f"{account.lower()}_price"
#     return getattr(scraped_data, account_price_field, 'N/A')