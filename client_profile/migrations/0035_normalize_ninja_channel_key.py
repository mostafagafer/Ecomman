from django.db import migrations


def normalize_ninja_channel_key(apps, schema_editor):
    Channel = apps.get_model("client_profile", "Channel")
    ProductChannel = apps.get_model("client_profile", "ProductChannel")

    legacy_channel = Channel.objects.filter(key="anan_isga").first()
    if not legacy_channel:
        return

    canonical_channel = Channel.objects.filter(key="ana_ninja").first()
    if canonical_channel:
        legacy_links = ProductChannel.objects.filter(channel=legacy_channel)
        for legacy_link in legacy_links:
            duplicate = ProductChannel.objects.filter(
                product_id=legacy_link.product_id,
                channel=canonical_channel,
            ).first()
            if duplicate:
                legacy_link.delete()
            else:
                legacy_link.channel = canonical_channel
                legacy_link.save(update_fields=["channel"])
        legacy_channel.delete()
    else:
        legacy_channel.key = "ana_ninja"
        legacy_channel.save(update_fields=["key"])


class Migration(migrations.Migration):

    dependencies = [
        ("client_profile", "0034_alter_channel_key"),
    ]

    operations = [
        migrations.RunPython(normalize_ninja_channel_key, migrations.RunPython.noop),
    ]
