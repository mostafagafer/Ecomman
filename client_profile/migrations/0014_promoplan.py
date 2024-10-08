# Generated by Django 5.0.7 on 2024-08-27 12:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_profile', '0013_productkeyword'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('discount_percentage', models.FloatField()),
                ('desired_price', models.FloatField(editable=False)),
                ('is_on_sale', models.BooleanField(default=False)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client_profile.product')),
            ],
        ),
    ]
