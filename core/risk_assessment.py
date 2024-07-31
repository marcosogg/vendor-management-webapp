from core import models
from django.db.models import Sum, Avg
from core.models import Vendor, Risk, Spend, Part


def calculate_risk_score(vendor):
    payment_terms_score = calculate_payment_terms_score(vendor.payment_terms)
    spend_score = calculate_spend_score(vendor)
    average_discount_score = calculate_average_discount_score(vendor)
    contract_score = calculate_contract_score(vendor.contract_year)
    relationship_type_score = calculate_relationship_type_score(
        vendor.relationship_type
    )

    total_score = (
        payment_terms_score
        + spend_score
        + average_discount_score
        + contract_score
        + relationship_type_score
    )

    risk_level = get_risk_level(total_score)

    return {
        "risk_level": risk_level,
        "total_score": total_score,
        "payment_terms_score": payment_terms_score,
        "spend_score": spend_score,
        "average_discount_score": average_discount_score,
        "contract_score": contract_score,
        "relationship_type_score": relationship_type_score,
    }


def calculate_payment_terms_score(payment_terms):
    payment_terms = str(payment_terms)  # Ensure payment_terms is a string
    if payment_terms == "PPAY":
        return 0
    elif payment_terms.startswith("Net "):
        try:
            days = int(payment_terms.split()[1])
            return 35 if days >= 30 else 5
        except (IndexError, ValueError):
            return 5  # Default to low score if we can't parse the number
    else:
        return 5  # Default to low score for unknown terms


def calculate_spend_score(vendor):
    SPEND_THRESHOLD = 1000000  # Example threshold, adjust as needed
    total_spend = (
        Spend.objects.filter(vendor=vendor).aggregate(Sum("usd_amount"))[
            "usd_amount__sum"
        ]
        or 0
    )
    return 25 if total_spend > SPEND_THRESHOLD else 0


def calculate_average_discount_score(vendor):
    avg_discount = (
        Part.objects.filter(vendor=vendor).aggregate(Avg("discount"))["discount__avg"]
        or 0
    )
    return 15 if avg_discount > 0 else 0


def calculate_contract_score(contract_year):
    return 15 if contract_year else 0


def calculate_relationship_type_score(relationship_type):
    return 10 if relationship_type == "DIRECT" else 0


def get_risk_level(total_score):
    if total_score <= 30:
        return "LOW"
    elif total_score <= 70:
        return "MEDIUM"
    else:
        return "HIGH"


def update_vendor_risk(vendor):
    risk_data = calculate_risk_score(vendor)
    risk, created = Risk.objects.update_or_create(vendor=vendor, defaults=risk_data)
    return risk
