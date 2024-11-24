
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.conf import settings
from django.utils.translation import gettext_lazy 

# # Predefined dictionary for account names and their URL requirements
# ACCOUNT_URL_VALIDATIONS = {
#     'amazon': 'amzn.eu',
#     'dawa': 'al-dawaa.com',
#     'nahdi': 'nahdionline.com',
# }

ACCOUNT_KEY = ['amazon', 'dawa', 'nahdi', 'noon_sa']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    client = models.CharField(max_length=50)
    plan = models.IntegerField(blank=True, null=True)
    pinned_tables = models.ManyToManyField('PinnedTable', blank=True)

    def __str__(self):
        return str(self.user)

# class Account(models.Model):
#     name = models.CharField(max_length=100, choices=[(key, key) for key in ACCOUNT_URL_VALIDATIONS.keys()])
#     domain = models.URLField()  # Now this field is a URLField

#     def __str__(self):
#         return self.name

class Account_id(models.Model):
    name = models.CharField(max_length=100, choices=[(key, key) for key in ACCOUNT_KEY])

    def __str__(self):
        return self.name
    

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    def __str__(self):
        return self.name

class Product(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='products')
    TITLE = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    RSP = models.FloatField(null=True, blank=True)  # Allowing null and blank
    RSP_VAT = models.FloatField(null=True, blank=True)  # Allowing null and blank
    # accounts = models.ManyToManyField(Account, through='ProductAccountLink')
    accounts_id = models.ManyToManyField(Account_id, through='ProductAccountLinkId')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    is_competitor = models.BooleanField(default=False)  # Adding a new boolean field


    def __str__(self):
        return f"{self.TITLE}"

class ProductAccountLinkId(models.Model):
    product = models.ForeignKey(Product, related_name='account_id_links', on_delete=models.CASCADE)
    account = models.ForeignKey(Account_id, related_name='product_id_links', on_delete=models.CASCADE)
    identifier = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return f"{self.product.TITLE} - {self.account.name} - {self.identifier}"



# class ProductAccountLink(models.Model):
#     product = models.ForeignKey(Product, related_name='account_links', on_delete=models.CASCADE)
#     account = models.ForeignKey(Account, related_name='product_links', on_delete=models.CASCADE)
#     url = models.URLField()

#     def clean(self):
#         if hasattr(self, 'account') and self.account:
#             # Validate the URL based on the account name
#             account_name = self.account.name
#             required_domain = ACCOUNT_URL_VALIDATIONS.get(account_name)
#             if required_domain and required_domain not in self.url:
#                 raise ValidationError(f'The URL must contain "{required_domain}" for the account "{account_name}".')
#         elif not hasattr(self, 'account'):
#             raise ValidationError('Account is required')

#     def __str__(self):
#         return f"{self.product.TITLE} - {self.account.name}"
            

class PinnedTable(models.Model):
    table_name = models.CharField(max_length=100)

    def __str__(self):
        return self.table_name

def product_photo_upload_path(instance, filename):
    user_id = instance.product.profile.user.id
    product_title = slugify(instance.product.TITLE)
    return f'product_photo/{user_id}/{product_title}/{filename}'

class Photo(models.Model):
    product = models.ForeignKey(Product, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_photo_upload_path)

    def __str__(self):
        return str(self.image)



## promo manager
class PromoPlan(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='promo_plans')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='promo_plans')
    start_date = models.DateField()
    end_date = models.DateField()
    discount_percentage = models.FloatField()
    desired_price = models.FloatField(editable=False)
    is_on_sale = models.BooleanField(default=False, editable=False)  # Hidden from forms and auto-managed

    @property
    def duration(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    def clean(self):
        super().clean()

        # Check for overlapping promo plans for the same product
        overlapping_plans = PromoPlan.objects.filter(
            product=self.product,
            start_date__lt=self.end_date,  # Start date is before the end date of this promo
            end_date__gt=self.start_date   # End date is after the start date of this promo
        ).exclude(pk=self.pk)  # Exclude the current instance in case of updates

        if overlapping_plans.exists():
            raise ValidationError(gettext_lazy("This promo plan overlaps with an existing plan for this product."))

    def save(self, *args, **kwargs):
        # Perform validation before saving
        self.full_clean()

        # Set is_on_sale to True if the product has a promo plan
        self.is_on_sale = True
        
        # Calculate desired price if not already set
        if self.desired_price is None:
            discount_amount = (self.discount_percentage / 100) * self.product.RSP_VAT
            self.desired_price = self.product.RSP_VAT - discount_amount
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.TITLE} Promo Plan"



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

