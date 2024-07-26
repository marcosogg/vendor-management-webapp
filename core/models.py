# core/models.py
from django.db import models

class Vendor(models.Model):
    vendor_name = models.CharField(max_length=200)
    vendor_id = models.CharField(max_length=50, unique=True)
    payment_terms = models.CharField(max_length=100)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    contract_year = models.IntegerField()
    relationship_type = models.CharField(max_length=50)

    def __str__(self):
        return self.vendor_name

class Part(models.Model):
    part_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='parts')
    buyer = models.CharField(max_length=100)
    discount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.part_number

class Spend(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='spends')
    year = models.IntegerField()
    usd_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ['vendor', 'year']

    def __str__(self):
        return f"{self.vendor.vendor_name} - {self.year}"

class Risk(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name='risk')
    risk_level = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.vendor.vendor_name} - {self.risk_level}"
