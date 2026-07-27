from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("client_profile", "0033_rename_accounts_to_channels"),
        ("scrapper", "0027_alter_scrapeddata_amazon_shipping_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ScrapedBulkData",
        ),
        migrations.DeleteModel(
            name="ScrapedData",
        ),
        migrations.CreateModel(
            name="ScrapedData",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scraped_at", models.DateTimeField(auto_now_add=True)),
                ("matched_url", models.URLField(blank=True, max_length=1000, null=True)),
                ("name", models.CharField(blank=True, max_length=500, null=True)),
                ("price", models.FloatField(blank=True, null=True)),
                ("original_price", models.FloatField(blank=True, null=True)),
                ("discount", models.FloatField(blank=True, null=True)),
                ("availability", models.IntegerField(blank=True, null=True)),
                ("image_url", models.URLField(blank=True, max_length=1000, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("sku", models.CharField(blank=True, max_length=300, null=True)),
                ("confidence", models.FloatField(default=0)),
                ("extraction_issues", models.JSONField(blank=True, default=list)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("success", "Success"),
                            ("no_evidence", "No Evidence"),
                            ("failed", "Failed"),
                        ],
                        default="success",
                        max_length=20,
                    ),
                ),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "channel",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scraped_results", to="client_profile.channel"),
                ),
                (
                    "product",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scraped_results", to="client_profile.product"),
                ),
                (
                    "product_channel",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scraped_results", to="client_profile.productchannel"),
                ),
            ],
            options={
                "ordering": ["-scraped_at"],
                "indexes": [
                    models.Index(fields=["product", "channel", "-scraped_at"], name="scrapper_sc_product_7dba86_idx"),
                    models.Index(fields=["product_channel", "-scraped_at"], name="scrapper_sc_product_ec6395_idx"),
                ],
            },
        ),
    ]
