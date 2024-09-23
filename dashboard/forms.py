from django import forms
from client_profile.models import Category, Subcategory, Brand, Product

class FilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select  # Dropdown for Category
    )
    subcategory = forms.ModelChoiceField(
        queryset=Subcategory.objects.all(),
        required=False,
        widget=forms.Select  # Dropdown for Subcategory
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        widget=forms.Select  # Dropdown for Brand
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select  # Dropdown for Product
    )

# from django import forms
# from client_profile.models import Product

# TIME_PERIOD_CHOICES = [
#     ('1_day', '1 Day'),
#     ('1_week', '1 Week'),
#     ('1_month', '1 Month'),
#     ('3_months', '3 Months'),
#     ('6_months', '6 Months'),
#     ('1_year', '1 Year'),
# ]

# class TimePeriodForm(forms.Form):
#     product = forms.ModelChoiceField(queryset=Product.objects.none())
#     time_period = forms.ChoiceField(choices=TIME_PERIOD_CHOICES)

#     def __init__(self, *args, **kwargs):
#         profile = kwargs.pop('profile')
#         super().__init__(*args, **kwargs)
#         self.fields['product'].queryset = Product.objects.filter(profile=profile)
