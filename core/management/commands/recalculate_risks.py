from django.core.management.base import BaseCommand
from core.models import Vendor
from core.risk_assessment import update_vendor_risk


class Command(BaseCommand):
    help = "Recalculates risk for all vendors"

    def handle(self, *args, **options):
        vendors = Vendor.objects.all()
        total = vendors.count()

        self.stdout.write(f"Recalculating risks for {total} vendors...")

        for i, vendor in enumerate(vendors, 1):
            risk = update_vendor_risk(vendor)
            self.stdout.write(
                f"[{i}/{total}] Updated risk for {vendor.vendor_name}: {risk.risk_level}"
            )

        self.stdout.write(
            self.style.SUCCESS("Risk recalculation completed successfully.")
        )
