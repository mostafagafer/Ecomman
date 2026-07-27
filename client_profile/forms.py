from django import forms
from django.forms import inlineformset_factory
from .models import Profile, Product, ProductChannel, Photo, Channel, PromoPlan #, Keyword, ProductKeyword, Account, ProductAccountLink
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields= ['username','first_name','last_name','email'] 

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['client','plan']
        
class ProductChannelForm(forms.ModelForm):
    channel = forms.ModelChoiceField(queryset=Channel.objects.all(), required=True)

    class Meta:
        model = ProductChannel
        fields = ['channel', 'search_name', 'known_product_url', 'is_enabled']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['channel'].label = 'Channel'
        self.fields['search_name'].label = 'Search name'
        self.fields['known_product_url'].label = 'Known product URL'
        self.fields['is_enabled'].label = 'Enabled'

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('channel'):
            self.add_error('channel', 'Channel is required')
        return cleaned_data

ProductChannelFormSet = inlineformset_factory(
    Product,
    ProductChannel,
    form=ProductChannelForm,
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
    brand_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brand', 'list': 'brand-options'}),
    )
    category_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category', 'list': 'category-options'}),
    )
    subcategory_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subcategory', 'list': 'subcategory-options'}),
    )

    class Meta:
        model = Product
        fields = ['is_competitor', 'product_name', 'description', 'RSP', 'RSP_VAT']
        widgets = {
            'is_competitor': forms.HiddenInput(),
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe this product clearly for matching and listings'}),
            'RSP': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'RSP_VAT': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        if instance and instance.pk:
            self.fields['brand_name'].initial = instance.brand.name if instance.brand else ''
            self.fields['category_name'].initial = instance.category.name if instance.category else ''
            self.fields['subcategory_name'].initial = instance.subcategory.name if instance.subcategory else ''
