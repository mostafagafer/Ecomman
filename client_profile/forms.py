from django import forms
from django.forms import inlineformset_factory
from .models import Profile, Product, ProductAccountLink, Photo, Account, PromoPlan #, Keyword, ProductKeyword
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields= ['username','first_name','last_name','email'] 

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['client','plan']
        

class ProductAccountLinkForm(forms.ModelForm):
    account = forms.ModelChoiceField(queryset=Account.objects.all(), required=True)

    class Meta:
        model = ProductAccountLink
        fields = ['account', 'url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].label = 'Account (required)'

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('account'):
            self.add_error('account', 'Account is required')
        return cleaned_data

ProductAccountLinkFormSet = inlineformset_factory(
    Product,
    ProductAccountLink,
    form=ProductAccountLinkForm,
    extra=1,
    can_delete=True
)

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image', 'image_description']

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
        fields = ['ASIN', 'TITLE', 'description', 'RSP', 'RSP_VAT', 'category', 'subcategory', 'brand']
# from django import forms
# from django.forms import inlineformset_factory
# from .models import Profile, Product, ProductAccountLink, Photo, Account, ACCOUNT_URL_REQUIREMENTS  
# from django.contrib.auth.models import User

# class UserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields= ['username','first_name','last_name','email'] 

# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ['client','plan']
        

# class ProductAccountLinkForm(forms.ModelForm):
#     account = forms.ModelChoiceField(queryset=Account.objects.all())

#     class Meta:
#         model = ProductAccountLink
#         fields = ['account', 'url']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['account'].required = True


    

#     def clean(self):
#         cleaned_data = super().clean()
#         account = cleaned_data.get('account')
#         if account is None:
#             return cleaned_data
#         account_id = account.account_id
#         url = cleaned_data.get('url')
#         if url is None:
#             self.add_error('url', 'This field cannot be empty.')
#             return cleaned_data
#         required_domain = ACCOUNT_URL_REQUIREMENTS.get(account_id)
#         if required_domain and required_domain not in url:
#             self.add_error('url', f'The URL must contain "{required_domain}" for the account "{account_id}".')
#         return cleaned_data

    

# ProductAccountLinkFormSet = inlineformset_factory(Product, ProductAccountLink, form=ProductAccountLinkForm, extra=1, can_delete=True)

# class PhotoForm(forms.ModelForm):
#     class Meta:
#         model = Photo
#         fields = ['image', 'image_description']

# PhotoFormSet = inlineformset_factory(Product, Photo, form=PhotoForm, extra=1, can_delete=True)

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['ASIN', 'TITLE', 'description', 'RSP', 'RSP_VAT']
# # from django import forms
# # # from django.contrib.auth.forms import UserCreationForm
# # from django.contrib.auth.models import User
# # from .models import Profile, Product, Photo
# # from django.forms import inlineformset_factory


# # # class SignupForm(UserCreationForm):
# # #     class Meta:
# # #         model = User
# # #         fields = ['username','email','password1','password2']

# # class UserForm(forms.ModelForm):
# #     class Meta:
# #         model = User
# #         fields= ['username','first_name','last_name','email'] 


# # class ProfileForm(forms.ModelForm):
# #     class Meta:
# #         model = Profile
# #         fields = ['client','plan']
        
# # class ProductForm(forms.ModelForm):
# #     class Meta:
# #         model = Product
# #         fields = ['ASIN', 'TITLE','description', 'RSP', 'RSP_VAT', 'Amazon_Link', 'Nahdi_Link', 'Dawa_Link']

# # class PhotoForm(forms.ModelForm):
# #     class Meta:
# #         model = Photo
# #         fields = ['image', 'image_description']

# # PhotoFormSet = inlineformset_factory(Product, Photo, form=PhotoForm, extra=1, can_delete=True)
