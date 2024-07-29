from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Vendor(models.Model):
    vendor_name = models.CharField(max_length=200)
    vendor_id = models.CharField(max_length=50, unique=True)
    payment_terms = models.CharField(max_length=100)
    credit_limit = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    contract_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    relationship_type = models.CharField(
        max_length=50,
        choices=[
            ("DIRECT", "Direct"),
            ("THIRD PARTY", "Third Party"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor_name} ({self.vendor_id})"


class Part(models.Model):
    part_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="parts")
    buyer = models.CharField(max_length=100)
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.part_number} - {self.vendor.vendor_name}"


class Spend(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="spends")
    year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    usd_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["vendor", "year"]


class Risk(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name="risk")
    risk_level = models.CharField(
        max_length=50, choices=[("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.vendor_name} - Risk: {self.get_risk_level_display()}"


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    details = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
