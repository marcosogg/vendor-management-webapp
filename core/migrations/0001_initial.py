# Generated by Django 5.0.7 on 2024-07-26 11:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('supplier_id', models.CharField(max_length=50, unique=True)),
                ('contact_email', models.EmailField(max_length=254)),
                ('contact_phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('credit_limit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('contract_year', models.IntegerField()),
                ('relationship_type', models.CharField(choices=[('Third Party', 'Third Party'), ('Direct', 'Direct')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Risk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('risk_level', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], max_length=10)),
                ('assessment_date', models.DateField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('supplier', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='risk', to='core.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_number', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('part_type', models.CharField(choices=[('Physical', 'Physical Gift Card'), ('E-code', 'E-code')], max_length=20)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='core.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='Spend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('payment_terms', models.CharField(max_length=50)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spends', to='core.supplier')),
            ],
            options={
                'unique_together': {('supplier', 'year')},
            },
        ),
    ]
