from django.db import models

from client_profile.models import Channel, Product, ProductChannel


class ScrapedData(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('no_evidence', 'No Evidence'),
        ('failed', 'Failed'),
    ]

    product = models.ForeignKey(Product, related_name='scraped_results', on_delete=models.CASCADE)
    product_channel = models.ForeignKey(ProductChannel, related_name='scraped_results', on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, related_name='scraped_results', on_delete=models.CASCADE)
    scraped_at = models.DateTimeField(auto_now_add=True)

    matched_url = models.URLField(max_length=1000, blank=True, null=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    original_price = models.FloatField(blank=True, null=True)
    discount = models.FloatField(blank=True, null=True)
    availability = models.IntegerField(blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=300, blank=True, null=True)
    confidence = models.FloatField(default=0)
    extraction_issues = models.JSONField(default=list, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['product', 'channel', '-scraped_at']),
            models.Index(fields=['product_channel', '-scraped_at']),
        ]

    def __str__(self):
        return f"{self.product.product_name} - {self.channel.display_name} - {self.scraped_at}"
