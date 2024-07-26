from django import forms
from .models import Vendor, Part, Spend, Risk

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_id', 'payment_terms', 'credit_limit', 'contract_year', 'relationship_type']

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['part_number', 'vendor', 'buyer', 'discount']

class SpendForm(forms.ModelForm):
    class Meta:
        model = Spend
        fields = ['vendor', 'year', 'usd_amount']

class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ['vendor', 'risk_level']
