from django.db import models
from django.db.models import Avg, Sum
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Vendor(models.Model):
    RELATIONSHIP_TYPE_CHOICES = [
        ("DIRECT", "Direct"),
        ("THIRD PARTY", "Third Party"),
    ]

    CONTRACT_TYPE_CHOICES = [
        ("FIXED", "Fixed Price"),
        ("TIME", "Time and Materials"),
        ("COST", "Cost Plus"),
    ]

    vendor_name = models.CharField(max_length=200)
    vendor_id = models.CharField(max_length=50, unique=True)
    payment_terms = models.CharField(max_length=100)
    country = models.CharField(max_length=2, blank=True, null=True)
    average_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    contract_type = models.CharField(
        max_length=10,
        choices=CONTRACT_TYPE_CHOICES,
        default="FIXED",
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    credit_limit = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    contract_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    relationship_type = models.CharField(
        max_length=50,
        choices=RELATIONSHIP_TYPE_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.payment_terms = str(self.payment_terms)
        super().save(*args, **kwargs)

    def update_performance_metrics(self):
        # Update average discount
        avg_discount = self.parts.aggregate(Avg("discount"))["discount__avg"]
        self.average_discount = avg_discount if avg_discount is not None else 0

        # Update rating based on spend
        current_year = timezone.now().year
        total_spend = self.spends.filter(year=current_year).aggregate(
            Sum("usd_amount")
        )["usd_amount__sum"]
        if total_spend:
            # This is a simple rating calculation, you might want to adjust it based on your specific requirements
            self.rating = min(
                5, total_spend / 1000000
            )  # 1 point for every million spent, max 5
        else:
            self.rating = 0

        self.save()

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
    relationship_type = models.CharField(
        max_length=50,
        choices=Vendor.RELATIONSHIP_TYPE_CHOICES,
        default="DIRECT",
    )
    rank = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["vendor", "year"]

    def __str__(self):
        return f"{self.vendor.vendor_name} - {self.year}: ${self.usd_amount}"

    def save(self, *args, **kwargs):
        # Ensure relationship_type matches the vendor's relationship_type
        self.relationship_type = self.vendor.relationship_type
        super().save(*args, **kwargs)


class Risk(models.Model):
    vendor = models.OneToOneField(Vendor, on_delete=models.CASCADE, related_name="risk")
    risk_level = models.CharField(
        max_length=50,
        choices=[("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High")],
        default="MEDIUM",
    )
    total_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], default=0
    )
    payment_terms_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(35)], default=0
    )
    spend_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(25)], default=0
    )
    average_discount_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(15)], default=0
    )
    contract_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(15)], default=0
    )
    relationship_type_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)], default=0
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.vendor_name} - Risk: {self.get_risk_level_display()}"


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    details = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
