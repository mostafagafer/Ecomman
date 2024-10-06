# # dashboard/models.py
# from django.db import models
# from django.utils import timezone
# from scrapper.models import ScrapedData

# class PerformanceData(models.Model):
#     scraped_data = models.ForeignKey(ScrapedData, on_delete=models.CASCADE, related_name='performance_data')
#     product = models.CharField(max_length=100)
#     pds = models.FloatField(default=0)
#     pcs = models.FloatField(default=0)
#     opps = models.FloatField(default=0)
#     scraped_at = models.DateTimeField(default=timezone.now)
#     amazon_sold_by = models.CharField(max_length=20, blank=True, null=True)
#     compliance_flags = models.JSONField(default=dict)
#     user_accounts = models.JSONField(default=list)
#     on_promo = models.BooleanField(default=False)
#     my_price = models.FloatField(default=0)

#     def __str__(self):
#         return f"Performance Data for {self.product} at {self.scraped_at}"
