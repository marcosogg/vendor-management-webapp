# Generated by Django 5.0.7 on 2024-07-31 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_vendor_average_discount_vendor_contract_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='spend',
            name='rank',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
