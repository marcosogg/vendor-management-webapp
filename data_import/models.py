# data_import/models.py

from django.db import models


class DiscountImport(models.Model):
    part_number = models.CharField(max_length=50)
    discount = models.DecimalField(max_digits=5, decimal_places=2)


class SpendImport(models.Model):
    vendor_id = models.CharField(max_length=50)
    usd_amount = models.DecimalField(max_digits=12, decimal_places=2)
    year = models.IntegerField()


class VendorImport(models.Model):
    part_number = models.CharField(max_length=50)
    vendor_id = models.CharField(max_length=50)
    vendor = models.CharField(max_length=200)
    buyer = models.CharField(max_length=100)
    payment_terms = models.CharField(max_length=100)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    contract_year = models.IntegerField()
    relationship_type = models.CharField(max_length=50)
    contract_type = models.CharField(max_length=10, default="FIXED")  # Add this line

    def __str__(self):
        return f"{self.vendor} ({self.vendor_id})"
