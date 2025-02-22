from django.db import models
from client_profile.models import Product, PromoPlan
from django.utils.functional import cached_property

class ScrapedData(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    scraped_at = models.DateTimeField(auto_now_add=True)

    # Amazon attributes 
    amazon_price = models.FloatField(blank=True, null=True)
    amazon_shipping = models.CharField(max_length=200, blank=True, null=True)
    amazon_sold_by = models.CharField(max_length=200, blank=True, null=True)
    amazon_title = models.CharField(max_length=500, blank=True, null=True)
    amazon_availability_info = models.CharField(max_length=200, blank=True, null=True)
    amazon_discount = models.FloatField(blank=True, null=True)
    amazon_sold_count = models.CharField(max_length=200, blank=True, null=True)
    amazon_choice = models.BooleanField(default=False)
    
    # Dawa attributes
    dawa_price = models.FloatField(blank=True, null=True)
    dawa_title = models.CharField(max_length=500, blank=True, null=True)
    dawa_availability_info = models.IntegerField(blank=True, null=True)
    dawa_original_price = models.FloatField(blank=True, null=True)
    dawa_is_in_stock_msi = models.IntegerField(blank=True, null=True)
    dawa_offer_text_notag = models.CharField(max_length=200, blank=True, null=True)
    dawa_discount = models.FloatField(blank=True, null=True)

    # Nahdi attributes
    nahdi_price = models.FloatField(blank=True, null=True)
    nahdi_title = models.CharField(max_length=500, blank=True, null=True)
    nahdi_availability_info = models.IntegerField(blank=True, null=True)
    nahdi_original_price = models.FloatField(blank=True, null=True)
    nahdi_ordered_qty = models.FloatField(blank=True, null=True)
    nahdi_sold_out = models.CharField(max_length=200, blank=True, null=True)
    nahdi_limited_stock = models.CharField(max_length=50, blank=True, null=True)
    nahdi_discount = models.FloatField(blank=True, null=True)

    # Noon_SA attributes
    noon_sa_price = models.FloatField(blank=True, null=True)
    noon_sa_title = models.CharField(max_length=500, blank=True, null=True)
    noon_sa_availability_info = models.IntegerField(blank=True, null=True)
    noon_sa_original_price = models.FloatField(blank=True, null=True)
    noon_sa_discount = models.FloatField(blank=True, null=True)
    noon_sa_sold_by = models.CharField(max_length=200, blank=True, null=True)

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
        discount = self.discount_percentage / 100 if self.discount_percentage is not None else None
        return rsp_vat - (discount * rsp_vat) if rsp_vat is not None and discount is not None else None




    @cached_property
    def nahdi_ratio(self):
        if self.final_price is None or self.nahdi_price is None:
            return None
        ratio = self.nahdi_price / self.final_price
        return ratio

    @cached_property
    def nahdi_compliance_score(self):
        if self.final_price is None or self.nahdi_price is None:
            return False
        
        abs_diff = abs(self.final_price-self.nahdi_price)
        complience_score = (1-(abs_diff/(0.5*self.final_price)))

        return complience_score


    @cached_property
    def amazon_ratio(self):
        if self.final_price is None or self.amazon_price is None:
            return None
        ratio = self.amazon_price / self.final_price
        return ratio

    @cached_property
    def amazon_compliance_score(self):
        if self.final_price is None or self.amazon_price is None:
            return False
        
        abs_diff = abs(self.final_price-self.amazon_price)
        complience_score = (1-(abs_diff/(0.5*self.final_price)))

        return complience_score

    @cached_property
    def dawa_compliance_score(self):
        if self.final_price is None or self.dawa_price is None:
            return False
        
        abs_diff = abs(self.final_price-self.dawa_price)
        complience_score = (1-(abs_diff/(0.5*self.final_price)))

        return complience_score
    
    @cached_property
    def dawa_ratio(self):
        if self.final_price is None or self.dawa_price is None:
            return None
        ratio = self.dawa_price / self.final_price
        return ratio
    


    @cached_property
    def noon_sa_compliance_score(self):
        if self.final_price is None or self.noon_sa_price is None:
            return False
        
        abs_diff = abs(self.final_price-self.noon_sa_price)
        complience_score = (1-(abs_diff/(0.5*self.final_price)))

        return complience_score


    def calculate_compliance_flag(self, price):
        """
        Generalized method to calculate compliance flag for a given price.
        """
        if self.final_price is None or price is None:
            return False

        lower_limit = self.final_price * 0.9
        upper_limit = self.final_price * 1.1

        return lower_limit <= price <= upper_limit

    @cached_property
    def dawa_compliance_flag(self):
        """
        Specific compliance flag for Dawa price.
        """
        return self.calculate_compliance_flag(self.dawa_price)

    @cached_property
    def nahdi_compliance_flag(self):
        """
        Specific compliance flag for Nahdi price.
        """
        return self.calculate_compliance_flag(self.nahdi_price)

    @cached_property
    def amazon_compliance_flag(self):
        """
        Specific compliance flag for Amazon price.
        """
        return self.calculate_compliance_flag(self.amazon_price)

    @cached_property
    def noon_sa_compliance_flag(self):
        """
        Specific compliance flag for Noon price.
        """
        return self.calculate_compliance_flag(self.noon_sa_price)



    @cached_property
    def price_deviation_score(self):
        store_prices = [self.amazon_price, self.dawa_price, self.nahdi_price, self.noon_sa_price]
        store_prices = [price for price in store_prices if price is not None]
        
        # Ensure that final_price is not None or 0
        if not store_prices or self.final_price is None or self.final_price == 0:
            return None  # Or return 0 if you prefer a numeric result instead of None
        
        # Calculate average deviation
        average_deviation = sum(abs(price - self.final_price) for price in store_prices) / len(store_prices)

        # Calculate Price Deviation Score (PDS)
        pds = (average_deviation / self.final_price) * 100

        return pds


    @cached_property
    def pcs(self):
        total_stores = sum(1 for price in [self.amazon_price, 
                                           self.dawa_price, 
                                           self.nahdi_price,
                                           self.noon_sa_price] if price is not None)
        compliant_stores = sum(1 for flag in [self.amazon_compliance_flag, 
                                              self.dawa_compliance_flag, 
                                              self.nahdi_compliance_flag, 
                                              self.noon_sa_compliance_flag] if flag)
        
        if total_stores == 0:
            return 0
        
        return (compliant_stores / total_stores) * 100

    @cached_property
    def account_deviation_score(self):
        """Calculates the average deviation score (ADS) from all compliance scores."""
        compliance_scores = [
            self.amazon_compliance_score,
            self.dawa_compliance_score,
            self.nahdi_compliance_score,
            self.noon_sa_compliance_score
        ]
        
        # Filter out None values and calculate the average
        valid_scores = [score for score in compliance_scores if score is not None]
        
        if valid_scores:
            return (sum(valid_scores) / len(valid_scores))*100
        return None  # Return None if no valid scores


    @cached_property
    def opps(self):
        price_deviation_score = self.price_deviation_score if self.price_deviation_score is not None else None
        account_deviation_score = self.account_deviation_score if self.account_deviation_score is not None else None
        return ((100 - price_deviation_score) + account_deviation_score) / 2 if price_deviation_score is not None and account_deviation_score is not None else None

    def __str__(self):
        # Gather all details in a list for clarity and manage None cases directly within formatting
        details = [
            f"Scraped data for Product {self.product.TITLE}",

            f"Amazon Price: {self.amazon_price if self.amazon_price is not None else 'N/A'}",
            f"Amazon Shipping: {self.amazon_shipping if self.amazon_shipping is not None else 'N/A'}",
            f"Amazon Sold By: {self.amazon_sold_by if self.amazon_sold_by is not None else 'N/A'}",
            f"Amazon Title: {self.amazon_title if self.amazon_title else 'N/A'}",
            f"Amazon Availability: {self.amazon_availability_info if self.amazon_availability_info else 'N/A'}",
            f"Amazon Discount: {self.amazon_discount if self.amazon_discount is not None else 'N/A'}",
            f"Amazon Sold Count: {self.amazon_sold_count if self.amazon_sold_count else 'N/A'}",
            f"Amazon Choice: {'Yes' if self.amazon_choice else 'No'}"

            f"Dawa Price: {self.dawa_price if self.dawa_price is not None else 'N/A'}",
            f"Dawa Title: {self.dawa_title if self.dawa_title else 'N/A'}",
            f"Dawa Availability Info: {self.dawa_availability_info if self.dawa_availability_info is not None else 'N/A'}",
            f"Dawa Original Price: {self.dawa_original_price if self.dawa_original_price is not None else 'N/A'}",
            f"Dawa In Stock MSI: {self.dawa_is_in_stock_msi if self.dawa_is_in_stock_msi is not None else 'N/A'}",
            f"Dawa Offer Text: {self.dawa_offer_text_notag if self.dawa_offer_text_notag else 'N/A'}",
            f"Dawa Discount: {self.dawa_discount if self.dawa_discount else 'N/A'}",

            f"Nahdi Price: {self.nahdi_price if self.nahdi_price is not None else 'N/A'}",
            f"Nahdi Title: {self.nahdi_title if self.nahdi_title else 'N/A'}",
            f"Nahdi Availability Info: {self.nahdi_availability_info if self.nahdi_availability_info is not None else 'N/A'}",
            f"Nahdi Original Price: {self.nahdi_original_price if self.nahdi_original_price is not None else 'N/A'}",
            f"Nahdi Ordered Quantity: {self.nahdi_ordered_qty if self.nahdi_ordered_qty is not None else 'N/A'}",
            f"Nahdi Sold Out: {self.nahdi_sold_out if self.nahdi_sold_out else 'N/A'}",
            f"Nahdi Limited Stock: {self.nahdi_limited_stock if self.nahdi_limited_stock else 'N/A'}",
            f"Nahdi Discount: {self.nahdi_discount if self.nahdi_discount else 'N/A'}",

            f"Noon_sa Title: {self.noon_sa_title if self.noon_sa_title else 'N/A'}",
            f"Noon_sa Availability Info: {self.noon_sa_availability_info if self.noon_sa_availability_info is not None else 'N/A'}",
            f"Noon_sa Original Price: {self.noon_sa_original_price if self.noon_sa_original_price is not None else 'N/A'}",
            f"Noon_sa Price: {self.noon_sa_price if self.noon_sa_price else 'N/A'}",
            f"Noon_sa Sold By: {self.noon_sa_sold_by if self.noon_sa_sold_by else 'N/A'}",
            f"Noon_sa Discount: {self.noon_sa_discount if self.noon_sa_discount else 'N/A'}",

            f"Promo Flag: {'Yes' if self.promo_flag else 'No'}",
            f"Discount Percentage: {self.discount_percentage:.2f}%",
            f"Final Price: {self.final_price:.2f}" if self.final_price else "Final Price: None",
            f"Price Deviation Score: {self.price_deviation_score:.2f}" if self.price_deviation_score is not None else "Price Deviation Score: N/A",
            f"Amazon Compliance Flag: {'Yes' if self.amazon_compliance_flag else 'No'}",
            f"Dawa Compliance Flag: {'Yes' if self.dawa_compliance_flag else 'No'}",
            f"Nahdi Compliance Flag: {'Yes' if self.nahdi_compliance_flag else 'No'}",
            f"Noon Compliance Flag: {'Yes' if self.noon_sa_compliance_flag else 'No'}",
            f"Amazon Compliance Ratio: {self.amazon_ratio:.2f}" if self.amazon_ratio is not None else "Amazon Compliance Ratio: N/A",
            f"Dawa Compliance Ratio: {self.dawa_ratio:.2f}" if self.dawa_ratio is not None else "Dawa Compliance Ratio: N/A",
            f"Nahdi Compliance Ratio: {self.nahdi_ratio:.2f}" if self.nahdi_ratio is not None else "Nahdi Compliance Ratio: N/A",
            f"Amazon Compliance Score: {self.amazon_compliance_score:.2f}" if self.amazon_compliance_score is not None else "Amazon Compliance Score: N/A",
            f"Dawa Compliance Score: {self.dawa_compliance_score:.2f}" if self.dawa_compliance_score is not None else "Dawa Compliance Score: N/A",
            f"Nahdi Compliance Sccore: {self.nahdi_compliance_score:.2f}" if self.nahdi_compliance_score is not None else "Nahdi Compliance Score: N/A",
            f"Noon Compliance Sccore: {self.noon_sa_compliance_score:.2f}" if self.noon_sa_compliance_score is not None else "Noon Compliance Score: N/A",
            f"Price Compliance Score: {self.pcs:.2f}%",
            f"ADS: {self.account_deviation_score:.2f} " if self.account_deviation_score is not None else "ADS: N/A"
            f"Online Price Performance Score: {self.opps:.2f}%"
        ]
        
        # Join details with commas for readability and return a single formatted string
        return ", ".join(details)


class ScrapedBulkData(models.Model):
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    scraped_at = models.DateTimeField(auto_now_add=True)

    # Store the search term as a simple string for clarity and flexibility
    key_name = models.CharField(max_length=100)  # Either the category or subcategory name

    # Amazon attributes 
    amazon_price = models.FloatField(blank=True, null=True)
    amazon_title = models.CharField(max_length=500, blank=True, null=True)
    amazon_sku = models.CharField(max_length=500, blank=True, null=True)
    amazon_original_price = models.FloatField(blank=True, null=True)
    amazon_discount = models.FloatField(blank=True, null=True)

    # Dawa attributes
    dawa_price = models.FloatField(blank=True, null=True)
    dawa_title = models.CharField(max_length=500, blank=True, null=True)
    dawa_sku = models.CharField(max_length=500, blank=True, null=True)
    dawa_original_price = models.FloatField(blank=True, null=True)
    dawa_offer_text_notag = models.CharField(max_length=200, blank=True, null=True)
    dawa_discount = models.FloatField(blank=True, null=True)

    # Nahdi attributes
    nahdi_price = models.FloatField(blank=True, null=True)
    nahdi_title = models.CharField(max_length=500, blank=True, null=True)
    nahdi_sku = models.CharField(max_length=500, blank=True, null=True)
    nahdi_original_price = models.FloatField(blank=True, null=True)
    nahdi_ordered_qty = models.FloatField(blank=True, null=True)
    nahdi_discount = models.FloatField(blank=True, null=True)

    # Noon_SA attributes
    noon_sa_price = models.FloatField(blank=True, null=True)
    noon_sa_title = models.CharField(max_length=500, blank=True, null=True)
    noon_sa_sku = models.CharField(max_length=500, blank=True, null=True)
    noon_sa_original_price = models.FloatField(blank=True, null=True)
    noon_sa_discount = models.FloatField(blank=True, null=True)



        

    def __str__(self):
        # Gather all details in a list for clarity and manage None cases directly within formatting
        details = [
            f"Scraped data for Key {self.key_name}",

            f"Amazon Price: {self.amazon_price if self.amazon_price is not None else 'N/A'}",
            f"Amazon Title: {self.amazon_title if self.amazon_title else 'N/A'}",
            f"Amazon SKU: {self.amazon_sku if self.amazon_sku else 'N/A'}",
            f"Amazon Discount: {self.amazon_discount if self.amazon_discount is not None else 'N/A'}",

            f"Dawa Price: {self.dawa_price if self.dawa_price is not None else 'N/A'}",
            f"Dawa Title: {self.dawa_title if self.dawa_title else 'N/A'}",
            f"Amazon SKU: {self.dawa_sku if self.dawa_sku else 'N/A'}",
            f"Dawa Original Price: {self.dawa_original_price if self.dawa_original_price is not None else 'N/A'}",
            f"Dawa Offer Text: {self.dawa_offer_text_notag if self.dawa_offer_text_notag else 'N/A'}",
            f"Dawa Discount: {self.dawa_discount if self.dawa_discount is not None else 'N/A'}",

            f"Nahdi Price: {self.nahdi_price if self.nahdi_price is not None else 'N/A'}",
            f"Nahdi Title: {self.nahdi_title if self.nahdi_title else 'N/A'}",
            f"Nahdi SKU: {self.nahdi_sku if self.nahdi_sku else 'N/A'}",
            f"Nahdi Original Price: {self.nahdi_original_price if self.nahdi_original_price is not None else 'N/A'}",
            f"Nahdi Ordered Quantity: {self.nahdi_ordered_qty if self.nahdi_ordered_qty is not None else 'N/A'}",
            f"Nahdi Discount: {self.nahdi_discount if self.nahdi_discount is not None else 'N/A'}",

            f"Noon_sa Title: {self.noon_sa_title if self.noon_sa_title else 'N/A'}",
            f"Noon_sa Original Price: {self.noon_sa_original_price if self.noon_sa_original_price is not None else 'N/A'}",
            f"Noon_sa SKU: {self.noon_sa_sku if self.noon_sa_sku else 'N/A'}",
            f"Noon_sa Price: {self.noon_sa_price if self.noon_sa_price else 'N/A'}",
            f"Noon_sa Discount: {self.noon_sa_discount if self.noon_sa_discount else 'N/A'}",

        ]
        
        # Join details with commas for readability and return a single formatted string
        return ", ".join(details)

