# core/management/commands/populate_db.py

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Vendor, Part, Spend, Risk
from django.utils import timezone
import random
from decimal import Decimal

class Command(BaseCommand):
    help = "Populates the database with sample data for testing"

    @transaction.atomic
    def handle(self, *args, **kwargs):0	494775.45	2024	DIRECT	2024-07-27 16:29:39.408634	2024-07-27 16:29:39.408634
    8	Staples Promotional (Accenture Store Card - USD)	STAPACUS	N30	1585622.2	2024	THIRD PARTY
        self.stdout.write("Populating database...")

        # Sample data
        sample_data = [
            ("EC00-1800FLOW-US-USD-25", "1800FL", "1800 FLOWERS", "B04", "N29"),
            ("EC00-1800FLOW-US-USD-50", "1800FL", "1800 FLOWERS", "B04", "N29"),
            (
                "EC00-1800PETS-US-USD-50",
                "PETSUN",
                "TABcom, LLC (DBA – petsupplies.com)",
                "B05",
                "N30",
            ),
            ("EC00-85CAFE-CN-CNY-20", "DATATR02", "DATATRADE LTD", "DAT", "FLOT"),
            (
                "EC00-A101-TR-TRY-1000",
                "SANMAG",
                "Bigbrands E-Ticket Hizmetleri ve ihract",
                "B08",
                "N5",
            ),
            (
                "EC00-A101-TR-TRY-250",
                "SANMAG",
                "Bigbrands E-Ticket Hizmetleri ve ihract",
                "B08",
                "N5",
            ),
            (
                "EC00-ABBVIE-US-USD-25",
                "BOUNDL",
                "Overture Promotions, Inc.",
                "B04",
                "N29",
            ),
            (
                "EC00-ACCENROW-US-USD-25",
                "BRANDA02",
                "Brand Addition (Accenture)",
                "B08",
                "N30",
            ),
            (
                "EC00-ACCENTUR-CA-CAD-25",
                "STAPACCA",
                "Staples Promotional Canada (Accenture Store Card)",
                "B08",
                "N30",
            ),
            (
                "EC00-ACCENTUR-US-USD-25",
                "STAPACUS",
                "Staples Promotional (Accenture Store Card - USD)",
                "B08",
                "N30",
            ),
        ]

        for part_number, vendor_id, vendor_name, buyer_id, terms in sample_data:
            # Create or update vendor
            vendor, _ = Vendor.objects.update_or_create(
                vendor_id=vendor_id,
                defaults={
                    "vendor_name": vendor_name,
                    "payment_terms": terms,
                    "credit_limit": Decimal(round(random.uniform(100000, 2000000), 2)),
                    "contract_year": timezone.now().year,
                    "relationship_type": random.choice(["DIRECT", "THIRD PARTY"]),
                },
            )

            # Create or update part
            Part.objects.update_or_create(
                part_number=part_number,
                defaults={
                    "vendor": vendor,
                    "buyer": buyer_id,
                    "discount": Decimal(round(random.uniform(0, 100), 2)),
                },
            )

            # Create or update spend data for the last 3 years
            current_year = timezone.now().year
            for year in range(current_year - 2, current_year + 1):
                Spend.objects.update_or_create(
                    vendor=vendor,
                    year=year,
                    defaults={
                        "usd_amount": Decimal(round(random.uniform(10000, 1000000), 2)),
                    },
                )

            # Create or update risk data
            Risk.objects.update_or_create(
                vendor=vendor,
                defaults={
                    "risk_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                },
            )

        self.stdout.write(self.style.SUCCESS("Database successfully populated!"))
