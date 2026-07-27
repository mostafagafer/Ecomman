from django.db import migrations, models
import django.db.models.deletion


CHANNEL_KEYS = {
    "amazon": "amazon_sa",
    "amazon_sa": "amazon_sa",
    "dawa": "al_dawa",
    "al_dawa": "al_dawa",
    "nahdi": "nahdi",
    "nice_one": "nice_one",
    "nice one": "nice_one",
    "anan_isga": "anan_isga",
    "anan isga": "anan_isga",
}

SEEDED_KEYS = ["amazon_sa", "al_dawa", "nahdi", "nice_one", "anan_isga"]


def normalize_channels(apps, schema_editor):
    Channel = apps.get_model("client_profile", "Channel")

    for channel in Channel.objects.all():
        old_name = (channel.name or "").strip().lower()
        channel.key = CHANNEL_KEYS.get(old_name, old_name.replace(" ", "_").replace("-", "_"))
        channel.save()

    for key in SEEDED_KEYS:
        Channel.objects.get_or_create(key=key)


class Migration(migrations.Migration):

    dependencies = [
        ("client_profile", "0032_alter_product_title"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Account_id",
            new_name="Channel",
        ),
        migrations.RenameModel(
            old_name="ProductAccountLinkId",
            new_name="ProductChannel",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="accounts_id",
            new_name="channels",
        ),
        migrations.RenameField(
            model_name="productchannel",
            old_name="account",
            new_name="channel",
        ),
        migrations.RenameField(
            model_name="channel",
            old_name="name",
            new_name="key",
        ),
        migrations.RenameField(
            model_name="productchannel",
            old_name="identifier",
            new_name="search_name",
        ),
        migrations.AlterField(
            model_name="channel",
            name="key",
            field=models.CharField(
                choices=[
                    ("amazon_sa", "Amazon SA"),
                    ("al_dawa", "Al-Dawa"),
                    ("nahdi", "Nahdi"),
                    ("nice_one", "Nice One"),
                    ("anan_isga", "Anan Isga"),
                ],
                max_length=50,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="productchannel",
            name="known_product_url",
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="productchannel",
            name="is_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="productchannel",
            name="last_scraped_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="product",
            name="channels",
            field=models.ManyToManyField(blank=True, through="client_profile.ProductChannel", to="client_profile.channel"),
        ),
        migrations.AlterField(
            model_name="productchannel",
            name="channel",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="product_channels", to="client_profile.channel"),
        ),
        migrations.AlterField(
            model_name="productchannel",
            name="product",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="product_channels", to="client_profile.product"),
        ),
        migrations.AlterField(
            model_name="productchannel",
            name="search_name",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.RunPython(normalize_channels, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="productchannel",
            constraint=models.UniqueConstraint(fields=("product", "channel"), name="unique_product_channel"),
        ),
    ]
