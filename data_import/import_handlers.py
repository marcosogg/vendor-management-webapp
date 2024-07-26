import pandas as pd
from core.models import Vendor, Part, Spend, Risk

def handle_uploaded_file(file):
    # Determine file type and read accordingly
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format")

    # Process the data
    records_imported = 0
    for _, row in df.iterrows():
        # This is a simplified example. You'll need to adapt this to your specific data structure.
        vendor, created = Vendor.objects.get_or_create(
            vendor_id=row['vendor_id'],
            defaults={
                'vendor_name': row['vendor_name'],
                'payment_terms': row['payment_terms'],
                'credit_limit': row['credit_limit'],
                'contract_year': row['contract_year'],
                'relationship_type': row['relationship_type']
            }
        )
        if created:
            records_imported += 1

        # Similar processing for Part, Spend, and Risk models...

    return records_imported
