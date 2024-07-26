# core/management/commands/populate_db.py

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Vendor, Part, Spend, Risk
from django.utils import timezone
import random


class Command(BaseCommand):
    help = "Populates the database with sample data for testing"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Populating database...")

        # Create vendors
        vendors = []
        for i in range(20):
            vendor = Vendor.objects.create(
                vendor_name=f"Vendor {i+1}",
                vendor_id=f"V{i+1:03d}",
                payment_terms=random.choice(["Net 30", "Net 60", "Net 90"]),
                credit_limit=random.randint(10000, 1000000),
                contract_year=random.randint(2020, 2024),
                relationship_type=random.choice(
                    ["Strategic", "Preferred", "Approved", "New"]
                ),
            )
            vendors.append(vendor)

        # Create parts
        for i in range(100):
            Part.objects.create(
                part_number=f"P{i+1:04d}",
                vendor=random.choice(vendors),
                buyer=f"Buyer {random.randint(1, 5)}",
                discount=random.uniform(0, 0.3),
            )

        # Create spend data
        current_year = timezone.now().year
        for vendor in vendors:
            for year in range(current_year - 3, current_year + 1):
                Spend.objects.create(
                    vendor=vendor, year=year, usd_amount=random.randint(10000, 1000000)
                )

        # Create risk assessments
        for vendor in vendors:
            Risk.objects.create(
                vendor=vendor, risk_level=random.choice(["Low", "Medium", "High"])
            )

        self.stdout.write(self.style.SUCCESS("Database successfully populated!"))
