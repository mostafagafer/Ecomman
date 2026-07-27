
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy 


CHANNELS = {
    'amazon_sa': {
        'display_name': 'Amazon SA',
        'website_url': 'https://www.amazon.sa',
    },
    'al_dawa': {
        'display_name': 'Al-Dawa',
        'website_url': 'https://www.al-dawaa.com',
    },
    'nahdi': {
        'display_name': 'Nahdi',
        'website_url': 'https://www.nahdionline.com/en-sa',
    },
    'nice_one': {
        'display_name': 'Nice One',
        'website_url': 'https://niceonesa.com',
    },
    'ana_ninja': {
        'display_name': 'Ninja',
        'website_url': 'https://ananinja.com/sa/en',
    },
    'noon_sa': {
        'display_name': 'Noon SA',
        'website_url': 'https://www.noon.com/saudi-en/',
    },
}

CHANNEL_CHOICES = [
    (key, value['display_name'])
    for key, value in CHANNELS.items()
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    client = models.CharField(max_length=50)
    plan = models.IntegerField(blank=True, null=True)
    pinned_tables = models.ManyToManyField('PinnedTable', blank=True)

    def __str__(self):
        return str(self.user)


class Channel(models.Model):
    key = models.CharField(max_length=50, choices=CHANNEL_CHOICES, unique=True)

    @property
    def display_name(self):
        return CHANNELS.get(self.key, {}).get('display_name', self.key)

    @property
    def website_url(self):
        return CHANNELS.get(self.key, {}).get('website_url', '')

    def __str__(self):
        return self.display_name
    

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
    product_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    RSP = models.FloatField(null=True, blank=True)  # Allowing null and blank
    RSP_VAT = models.FloatField(null=True, blank=True)  # Allowing null and blank
    channels = models.ManyToManyField(Channel, through='ProductChannel', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    is_competitor = models.BooleanField(default=False)  
    # Self-referential ManyToManyField for competitor references
    competitor_references = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='referenced_by'
    )


    def __str__(self):
        return f"{self.product_name}"

class ProductChannel(models.Model):
    product = models.ForeignKey(Product, related_name='product_channels', on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, related_name='product_channels', on_delete=models.CASCADE)
    search_name = models.CharField(max_length=300, blank=True, null=True)
    known_product_url = models.URLField(max_length=1000, blank=True, null=True)
    is_enabled = models.BooleanField(default=True)
    last_scraped_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'channel'], name='unique_product_channel')
        ]

    @property
    def effective_search_name(self):
        return self.search_name or self.product.product_name

    def __str__(self):
        return f"{self.product.product_name} - {self.channel.display_name}"


            

class PinnedTable(models.Model):
    table_name = models.CharField(max_length=100)

    def __str__(self):
        return self.table_name

def product_photo_upload_path(instance, filename):
    user_id = instance.product.profile.user.id
    product_title = slugify(instance.product.product_name)
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
        return f"{self.product.product_name} Promo Plan"



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
