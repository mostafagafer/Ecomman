from django.contrib import admin

# Register your models here.
from .models import  ScrapedData #Product,

# admin.site.register(Product)
admin.site.register(ScrapedData)