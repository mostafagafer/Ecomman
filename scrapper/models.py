


from django.db import models
from client_profile.models import Product, PromoPlan
from django.contrib.auth.models import User
from django.utils.functional import cached_property
class ScrapedData(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    dawa_price = models.FloatField(blank=True, null=True)
    nahdi_price = models.FloatField(blank=True, null=True)
    amazon_price = models.FloatField(blank=True, null=True)
    amazon_shipping = models.CharField(max_length=20, blank=True, null=True)
    amazon_sold_by = models.CharField(max_length=20, blank=True, null=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    @cached_property
    def promo_flag(self):
        return PromoPlan.objects.filter(
            product=self.product,
            start_date__lte=self.scraped_at.date(),
            end_date__gte=self.scraped_at.date()
        ).exists()

    @cached_property
    def discount_percentage(self):
        promo_plan = PromoPlan.objects.filter(
            product=self.product,
            start_date__lte=self.scraped_at.date(),
            end_date__gte=self.scraped_at.date()
        ).first()
        return promo_plan.discount_percentage if promo_plan else 0

    @cached_property
    def final_price(self):
        rsp_vat = self.product.RSP_VAT
        discount = self.discount_percentage / 100
        return rsp_vat - (discount * rsp_vat)


    @cached_property
    def amazon_ratio(self):
        if self.final_price is None or self.amazon_price is None:
            return None
        ratio = self.amazon_price / self.final_price
        return ratio

    @cached_property
    def dawa_ratio(self):
        if self.final_price is None or self.dawa_price is None:
            return None
        ratio = self.dawa_price / self.final_price
        return ratio
    
    @cached_property
    def nahdi_ratio(self):
        if self.final_price is None or self.nahdi_price is None:
            return None
        ratio = self.nahdi_price / self.final_price
        return ratio

    @cached_property
    def amazon_compliance_flag(self):
        if self.final_price is None or self.amazon_price is None:
            return False
        
        lower_limit = self.final_price * 0.9
        upper_limit = self.final_price * 1.1

        return lower_limit <= self.amazon_price <= upper_limit

    @cached_property
    def dawa_compliance_flag(self):
        if self.final_price is None or self.dawa_price is None:
            return False
        
        lower_limit = self.final_price * 0.9
        upper_limit = self.final_price * 1.1

        return lower_limit <= self.dawa_price <= upper_limit

    @cached_property
    def nahdi_compliance_flag(self):
        if self.final_price is None or self.nahdi_price is None:
            return False
        
        lower_limit = self.final_price * 0.9
        upper_limit = self.final_price * 1.1

        return lower_limit <= self.nahdi_price <= upper_limit


    @cached_property
    def price_deviation_score(self):
        store_prices = [self.amazon_price, self.dawa_price, self.nahdi_price]
        store_prices = [price for price in store_prices if price is not None]
        
        if not store_prices or self.final_price == 0:
            return 0
        
        average_deviation = sum(abs(price - self.final_price) for price in store_prices) / len(store_prices)
        pds = (1 - (average_deviation / self.final_price)) * 100
        return pds
    
    @cached_property
    def pcs(self):
        total_stores = sum(1 for price in [self.amazon_price, self.dawa_price, self.nahdi_price] if price is not None)
        compliant_stores = sum(1 for flag in [self.amazon_compliance_flag, self.dawa_compliance_flag, self.nahdi_compliance_flag] if flag)
        
        if total_stores == 0:
            return 0
        
        return (compliant_stores / total_stores) * 100

    # @property
    # def pcs(self):
    #     # Calculate Price Compliance Score (PCS) as the average of non-None compliance scores
    #     compliance_flags = [
    #         self.amazon_compliance_flag,
    #         self.dawa_compliance_flag,
    #         self.nahdi_compliance_flag
    #     ]
    #     valid_flags = [flag for flag in compliance_flags if flag is not None]

    #     if not valid_flags:
    #         return 0  # Avoid division by zero

    #     return sum(valid_flags) / len(valid_flags)

    @cached_property
    def opps(self):
        opps = (self.price_deviation_score+self.pcs)/2
        return opps
        


    def __str__(self):
        return (
            f"Scraped data for Product {self.product.TITLE} "
            f"(ASIN: {self.product.ASIN}) at {self.scraped_at}: "
            f"Dawa Price: {self.dawa_price if self.dawa_price is not None else 'N/A'}, "
            f"Nahdi Price: {self.nahdi_price if self.nahdi_price is not None else 'N/A'}, "
            f"Amazon Price: {self.amazon_price if self.amazon_price is not None else 'N/A'}, "
            f"Amazon Shipping: {self.amazon_shipping if self.amazon_shipping else 'N/A'}, "
            f"Amazon Sold By: {self.amazon_sold_by if self.amazon_sold_by else 'N/A'}, "
            f"Promo Flag: {'Yes' if self.promo_flag else 'No'}, "
            f"Discount Percentage: {self.discount_percentage:.2f}%, "
            f"Final Price: {self.final_price:.2f}, "
            f"Price Deviation Score: {self.price_deviation_score:.2f}, "
            f"Amazon Compliance Flag: {'Yes' if self.amazon_compliance_flag else 'No'}, "
            f"Dawa Compliance Flag: {'Yes' if self.dawa_compliance_flag else 'No'}, "
            f"Nahdi Compliance Flag: {'Yes' if self.nahdi_compliance_flag else 'No'}, "
            f"Amazon Compliance Ratio: {self.amazon_ratio:.2f} " if self.amazon_ratio is not None else "Amazon Compliance Ratio: N/A, "
            f"Dawa Compliance Ratio: {self.dawa_ratio:.2f} " if self.dawa_ratio is not None else "Dawa Compliance Ratio: N/A, "
            f"Nahdi Compliance Ratio: {self.nahdi_ratio:.2f} " if self.nahdi_ratio is not None else "Nahdi Compliance Ratio: N/A, "
            f"Price Compliance Score: {self.pcs:.2f}%, "
            f"Online Price Performance Score: {self.opps:.2f}%, "


        )

# from django.db import models
# from client_profile.models import Product, PromoPlan
# from decimal import Decimal, ROUND_HALF_UP

# from django.db import models
# from decimal import Decimal, ROUND_HALF_UP
# from client_profile.models import Product, c

# class ScrapedData(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     dawa_price = models.FloatField(blank=True, null=True)
#     nahdi_price = models.FloatField(blank=True, null=True)
#     amazon_price = models.FloatField(blank=True, null=True)
#     amazon_shipping = models.CharField(max_length=20, blank=True, null=True)
#     amazon_sold_by = models.CharField(max_length=20, blank=True, null=True)
#     scraped_at = models.DateTimeField(auto_now_add=True)
#     final_desired_price = models.FloatField(blank=True, null=True)
#     discount_amount = models.FloatField(blank=True, null=True)
#     pds = models.FloatField(blank=True, null=True)
#     pcs = models.FloatField(blank=True, null=True)
#     opps = models.FloatField(blank=True, null=True)
#     amazon_compliance = models.BooleanField(default=False)
#     nahdi_compliance = models.BooleanField(default=False)
#     dawa_compliance = models.BooleanField(default=False)

#     def __str__(self):
#         return (
#             f"Scraped data for Product {self.product.TITLE} "
#             f"(ASIN: {self.product.ASIN}) at {self.scraped_at}: "
#             f"Dawa Price: {self.dawa_price if self.dawa_price is not None else 'N/A'}, "
#             f"Nahdi Price: {self.nahdi_price if self.nahdi_price is not None else 'N/A'}, "
#             f"Amazon Price: {self.amazon_price if self.amazon_price is not None else 'N/A'}, "
#             f"Amazon Shipping: {self.amazon_shipping if self.amazon_shipping else 'N/A'}, "
#             f"Amazon Sold By: {self.amazon_sold_by if self.amazon_sold_by else 'N/A'}"
#         )

#     def discount_amount(self):
#         try:
#             promo_plan = PromoPlan.objects.get(
#                 product=self.product,
#                 start_date__lte=self.scraped_at,
#                 end_date__gte=self.scraped_at
#             )
#             return (promo_plan.discount_percentage / 100) * self.product.RSP_VAT
#         except PromoPlan.DoesNotExist:
#             return 0.0

#     def calculate_final_desired_price(self):
#         # Query all products
#         product = self.product
        
#         # Check for applicable promo plans for this product within the timeline
#         promo_plans = PromoPlan.objects.filter(
#             product=product,
#             start_date__lte=self.scraped_at.date(),
#             end_date__gte=self.scraped_at.date()
#         )

#         if promo_plans.exists():
#             # Use the desired_price from any applicable promo plan
#             promo_plan = promo_plans.first()  # Get the first matching promo plan
#             final_price = promo_plan.desired_price
#         else:
#             # No promo plan is applicable, use RSP_VAT
#             final_price = product.RSP_VAT

#         return float(final_price)
    
#     # def calculate_final_desired_price(self):
#     #     try:
#     #         promo_plan = PromoPlan.objects.get(
#     #             product=self.product,
#     #             start_date__lte=self.scraped_at,
#     #             end_date__gte=self.scraped_at
#     #         )
#     #         return (promo_plan.discount_percentage / 100) * self.product.RSP_VAT
#     #     except PromoPlan.DoesNotExist:
#     #         return 0.0


#     def save(self, *args, **kwargs):
#         self.discount_amount = self.discount_amount


#         # Calculate the final desired price
#         self.final_desired_price = self.calculate_final_desired_price()

#         # Update compliance flags based on the final desired price
#         self.amazon_compliance = self.amazon_price and self.final_desired_price and (
#             self.amazon_price <= self.final_desired_price * 1.1 and self.amazon_price >= self.final_desired_price * 0.9
#         )
#         self.nahdi_compliance = self.nahdi_price and self.final_desired_price and (
#             self.nahdi_price <= self.final_desired_price * 1.1 and self.nahdi_price >= self.final_desired_price * 0.9
#         )
#         self.dawa_compliance = self.dawa_price and self.final_desired_price and (
#             self.dawa_price <= self.final_desired_price * 1.1 and self.dawa_price >= self.final_desired_price * 0.9
#         )

#         # Calculate PDS and PCS
#         store_prices = [self.amazon_price, self.nahdi_price, self.dawa_price]
#         self.pds = calculate_pds(self.final_desired_price, store_prices)
#         self.pcs = round(calculate_pcs(self.final_desired_price, store_prices), 2)
#         self.opps = round((self.pcs + self.pds) / 2, 2)

#         # Save the instance
#         super().save(*args, **kwargs)

# def calculate_pds(set_price, store_prices):
#     if not store_prices:
#         return 0
#     average_deviation = sum(abs(Decimal(price) - Decimal(set_price)) for price in store_prices) / len(store_prices)
#     pds = (1 - (average_deviation / Decimal(set_price))) * 100
#     pds = pds.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#     return float(pds)

# def calculate_pcs(set_price, store_prices, acceptable_range_percentage=10):
#     if not store_prices:
#         return 0
#     acceptable_range = set_price * (acceptable_range_percentage / 100)
#     compliant_stores = sum(1 for price in store_prices if set_price - acceptable_range <= price <= set_price + acceptable_range)
#     total_stores = len(store_prices)
#     pcs = (compliant_stores / total_stores) * 100
#     return pcs
