from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("client_profile", "0035_normalize_ninja_channel_key"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="TITLE",
            new_name="product_name",
        ),
    ]
