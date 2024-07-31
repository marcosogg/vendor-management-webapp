import pandas as pd
from django.db import transaction
from core.models import Vendor, Part, Spend, Risk
from .models import DiscountImport, SpendImport, VendorImport
from django.db import IntegrityError
from core.risk_assessment import update_vendor_risk


@transaction.atomic
def handle_uploaded_file(file, import_type):
    try:
        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file, engine="openpyxl")
        else:
            raise ValueError(
                "Unsupported file format. Please upload an Excel file (.xlsx)."
            )

        print(f"Columns in the uploaded file: {df.columns.tolist()}")
        print(f"First few rows of the data:\n{df.head()}")

        if import_type == "vendors":
            import_vendors(df)
        elif import_type == "parts":
            import_discount(df)
        elif import_type == "spend":
            import_spend(df)
        else:
            raise ValueError("Invalid import type")

        return len(df)
    except Exception as e:
        print(f"Error during file import: {str(e)}")
        raise


def import_discount(df):
    for _, row in df.iterrows():
        DiscountImport.objects.create(
            part_number=row["part_number"], discount=row["discount"]
        )

    for discount_import in DiscountImport.objects.all():
        Part.objects.filter(part_number=discount_import.part_number).update(
            discount=discount_import.discount
        )

    DiscountImport.objects.all().delete()


def import_spend(df):
    required_columns = ["vendor_id", "usd_amount", "year"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"The following required columns are missing: {', '.join(missing_columns)}"
        )

    for _, row in df.iterrows():
        SpendImport.objects.create(
            vendor_id=row["vendor_id"], usd_amount=row["usd_amount"], year=row["year"]
        )

    for spend_import in SpendImport.objects.all():
        vendor = Vendor.objects.filter(vendor_id=spend_import.vendor_id).first()
        if vendor:
            try:
                spend, created = Spend.objects.update_or_create(
                    vendor=vendor,
                    year=spend_import.year,
                    defaults={"usd_amount": spend_import.usd_amount},
                )
                if created:
                    print(
                        f"Created new Spend entry for vendor {vendor.vendor_name} in year {spend_import.year}"
                    )
                else:
                    print(
                        f"Updated existing Spend entry for vendor {vendor.vendor_name} in year {spend_import.year}"
                    )

                # Update risk assessment after spend import
                update_vendor_risk(vendor)
            except IntegrityError as e:
                print(f"Error creating/updating Spend entry: {str(e)}")
        else:
            print(f"Warning: No vendor found with ID {spend_import.vendor_id}")

    SpendImport.objects.all().delete()


@transaction.atomic
def import_vendors(df):
    required_columns = [
        "part_number",
        "vendor_id",
        "vendor",
        "buyer",
        "payment_terms",
        "credit_limit",
        "contract_year",
        "relationship_type",
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"The following required columns are missing: {', '.join(missing_columns)}"
        )

    for _, row in df.iterrows():
        VendorImport.objects.create(
            part_number=row["part_number"],
            vendor_id=row["vendor_id"],
            vendor=row["vendor"],
            buyer=row["buyer"],
            payment_terms=row["payment_terms"],
            credit_limit=row["credit_limit"],
            contract_year=row["contract_year"],
            relationship_type=row["relationship_type"],
        )

    for vendor_import in VendorImport.objects.all():
        vendor, _ = Vendor.objects.update_or_create(
            vendor_id=vendor_import.vendor_id,
            defaults={
                "vendor_name": vendor_import.vendor,
                "payment_terms": vendor_import.payment_terms,
                "credit_limit": vendor_import.credit_limit,
                "contract_year": vendor_import.contract_year,
                "relationship_type": vendor_import.relationship_type,
            },
        )

        Part.objects.update_or_create(
            part_number=vendor_import.part_number,
            defaults={
                "vendor": vendor,
                "buyer": vendor_import.buyer,
                "discount": 0,  # Default value, will be updated by discount import
            },
        )

        # Update risk assessment
        update_vendor_risk(vendor)

    VendorImport.objects.all().delete()
