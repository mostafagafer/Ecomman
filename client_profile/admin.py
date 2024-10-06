from django.contrib import admin
from .models import Profile, Product, Photo, Account, Account_id, ProductAccountLink, ProductAccountLinkId, Product, PromoPlan, Brand, Category, Subcategory #Keyword


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1

class ProductAccountLinkInline(admin.TabularInline):
    model = ProductAccountLink
    extra = 1

class ProductAccountLinkIdInline(admin.TabularInline):
    model = ProductAccountLinkId
    extra = 1


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1

class ProfileAdmin(admin.ModelAdmin):
    inlines = [ProductInline]

class ProductAdmin(admin.ModelAdmin):
    inlines = [PhotoInline, ProductAccountLinkInline, ProductAccountLinkIdInline] #, KeywordInline
    list_display = ('TITLE', 'description', 'RSP', 'RSP_VAT', 'profile', 'category', 'subcategory', 'brand')  # Add new fields
    list_filter = ('category', 'subcategory', 'brand')  # Add new filters
    search_fields = ('TITLE', 'description', 'category__name', 'subcategory__name', 'brand__name')  # Add new fields

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
    search_fields = ('name', 'product__TITLE')




admin.site.register(Profile, ProfileAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Photo)
admin.site.register(Account)
admin.site.register(Account_id)
admin.site.register(ProductAccountLink)
admin.site.register(ProductAccountLinkId)
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
