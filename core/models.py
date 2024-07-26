# core/models.py

from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    supplier_id = models.CharField(max_length=50, unique=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    contract_year = models.IntegerField()
    relationship_type = models.CharField(max_length=20, choices=[('Third Party', 'Third Party'), ('Direct', 'Direct')])

    def __str__(self):
        return self.name

class Part(models.Model):
    part_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='parts')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    part_type = models.CharField(max_length=20, choices=[('Physical', 'Physical Gift Card'), ('E-code', 'E-code')])

    def __str__(self):
        return f"{self.part_number} - {self.description}"

class Spend(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='spends')
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_terms = models.CharField(max_length=50)
    discount = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        unique_together = ('supplier', 'year')

    def __str__(self):
        return f"{self.supplier.name} - {self.year} - ${self.amount}"

class Risk(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE, related_name='risk')
    risk_level = models.CharField(max_length=10, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    assessment_date = models.DateField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.supplier.name} - Risk Level: {self.risk_level}"
