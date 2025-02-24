from django import forms
from django.forms import inlineformset_factory
from .models import Profile, Product, ProductAccountLinkId, Photo,Account_id, PromoPlan #, Keyword, ProductKeyword, Account, ProductAccountLink
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields= ['username','first_name','last_name','email'] 

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['client','plan']
        
class ProductAccountIdLinkForm(forms.ModelForm):
    account = forms.ModelChoiceField(queryset=Account_id.objects.all(), required=True)

    class Meta:
        model = ProductAccountLinkId
        fields = ['account', 'identifier']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].label = 'Account (required)'
        self.fields['identifier'].label = 'Identifier (required)'

    def clean(self):
        cleaned_data = super().clean()
        # Ensure account is selected
        if not cleaned_data.get('account'):
            self.add_error('account', 'Account is required')
        # Ensure identifier is provided
        if not cleaned_data.get('identifier'):
            self.add_error('identifier', 'Identifier is required')
        return cleaned_data

ProductAccountIdLinkFormSet = inlineformset_factory(
    Product,
    ProductAccountLinkId,
    form=ProductAccountIdLinkForm,
    extra=1,
    can_delete=True
)

# class ProductAccountLinkForm(forms.ModelForm):
#     account = forms.ModelChoiceField(queryset=Account.objects.all(), required=True)

#     class Meta:
#         model = ProductAccountLink
#         fields = ['account', 'url']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['account'].label = 'Account (required)'

#     def clean(self):
#         cleaned_data = super().clean()
#         if not cleaned_data.get('account'):
#             self.add_error('account', 'Account is required')
#         return cleaned_data

# ProductAccountLinkFormSet = inlineformset_factory(
#     Product,
#     ProductAccountLink,
#     form=ProductAccountLinkForm,
#     extra=1,
#     can_delete=True
# )

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image']

PhotoFormSet = inlineformset_factory(Product, Photo, form=PhotoForm, extra=1, can_delete=True)

# class KeywordForm(forms.Form):
#     keyword = forms.CharField(max_length=100)

# class ProductKeywordForm(forms.ModelForm):
#     keyword = forms.CharField(max_length=100)

#     class Meta:
#         model = ProductKeyword
#         fields = ['keyword']

#     def save(self, commit=True):
#         # Get or create the Keyword instance
#         keyword, created = Keyword.objects.get_or_create(name=self.cleaned_data['keyword'])
#         # Associate the keyword with the ProductKeyword instance
#         self.instance.keyword = keyword
#         if commit:
#             self.instance.save()
#         return self.instance

# ProductKeywordFormSet = inlineformset_factory(
#     Product,
#     ProductKeyword,
#     form=ProductKeywordForm,
#     extra=1,
#     can_delete=True
# )

# Promo manager
class PromoPlanForm(forms.ModelForm):
    class Meta:
        model = PromoPlan
        fields = ['product', 'start_date', 'end_date', 'discount_percentage']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'id': 'id_start_date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'id': 'id_end_date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PromoPlanForm, self).__init__(*args, **kwargs)
        if user:
            # Filter products by the user's profile
            self.fields['product'].queryset = Product.objects.filter(profile=user.profile)



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['TITLE', 'description', 'RSP', 'RSP_VAT', 'category', 'subcategory', 'brand']
