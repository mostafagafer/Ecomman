# Generated by Django 5.0.7 on 2024-08-18 12:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrapper', '0002_scrapeddata_pinned_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scrapeddata',
            name='pinned_by',
        ),
        migrations.CreateModel(
            name='PinnedTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_name', models.CharField(max_length=255)),
                ('data', models.JSONField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pinned_tables', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
