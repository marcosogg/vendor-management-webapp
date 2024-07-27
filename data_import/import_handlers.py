import pandas as pd
from django.db import transaction
from core.models import Vendor, Part, Spend, Risk


@transaction.atomic
def handle_uploaded_file(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format")

    records_imported = 0
    errors = []

    for _, row in df.iterrows():
        try:
            vendor, created = Vendor.objects.update_or_create(
                vendor_id=row["vendor_id"],
                defaults={
                    "vendor_name": row["vendor_name"],
                    "payment_terms": row["payment_terms"],
                    "credit_limit": row["credit_limit"],
                    "contract_year": row["contract_year"],
                    "relationship_type": row["relationship_type"],
                },
            )

            if "part_number" in row:
                Part.objects.update_or_create(
                    part_number=row["part_number"],
                    defaults={
                        "vendor": vendor,
                        "buyer": row["buyer"],
                        "discount": row["discount"],
                    },
                )

            if "spend_year" in row and "spend_amount" in row:
                Spend.objects.update_or_create(
                    vendor=vendor,
                    year=row["spend_year"],
                    defaults={"usd_amount": row["spend_amount"]},
                )

            if "risk_level" in row:
                Risk.objects.update_or_create(
                    vendor=vendor, defaults={"risk_level": row["risk_level"]}
                )

            records_imported += 1
        except Exception as e:
            errors.append(f"Error in row {_}: {str(e)}")

    return records_imported, errors
