# Generated by Django 5.0.7 on 2024-12-30 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0026_alter_scrapedbulkdata_amazon_sku_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapeddata',
            name='amazon_shipping',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='scrapeddata',
            name='amazon_sold_by',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='scrapeddata',
            name='nahdi_sold_out',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='scrapeddata',
            name='noon_sa_sold_by',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
