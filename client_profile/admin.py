from django.contrib import admin
from .models import Profile, Product, Photo, Channel, ProductChannel, Product, PromoPlan, Brand, Category, Subcategory #Keyword, ProductAccountLink, Account


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

# class ProductAccountLinkInline(admin.TabularInline):
#     model = ProductAccountLink
#     extra = 1

class ProductChannelInline(admin.TabularInline):
    model = ProductChannel
    extra = 1


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1

class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProductInline]

class ProductAdmin(admin.ModelAdmin):
    inlines = [PhotoInline, ProductChannelInline] #, KeywordInline, ProductAccountLinkInline
    list_display = ('product_name', 'description', 'RSP', 'RSP_VAT', 'profile', 'category', 'subcategory', 'brand')  # Add new fields
    list_filter = ('category', 'subcategory', 'brand')  # Add new filters
    search_fields = ('product_name', 'description', 'category__name', 'subcategory__name', 'brand__name')  # Add new fields

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')  # Show the category relation
    list_filter = ('category',)
    search_fields = ('name',)

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class PromoPlanAdmin(admin.ModelAdmin):
    list_display = ('product', 'start_date', 'end_date', 'discount_percentage', 'desired_price', 'is_on_sale')
    list_filter = ('product__profile__user', 'start_date', 'end_date')
    search_fields = ('name', 'product__product_name')




admin.site.register(Profile, ProfileAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Photo)
admin.site.register(Channel)
admin.site.register(ProductChannel)
# admin.site.register(Keyword)
admin.site.register(PromoPlan, PromoPlanAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Brand, BrandAdmin)

####

# from django.contrib import admin
# from .models import Profile, Product, Photo, ProductAccountLink, Account

# class PhotoInline(admin.TabularInline):
#     model = Photo
#     extra = 1

# class ProductAccountLinkInline(admin.TabularInline):
#     model = ProductAccountLink
#     extra = 1

# class ProductAdmin(admin.ModelAdmin):
#     inlines = [PhotoInline, ProductAccountLinkInline]

# admin.site.register(Profile)
# admin.site.register(Product, ProductAdmin)
# admin.site.register(Photo)
# admin.site.register(Account)
