# data_import/admin.py

from django.contrib import admin
from .models import DiscountImport, SpendImport, VendorImport

admin.site.register(DiscountImport)
admin.site.register(SpendImport)
admin.site.register(VendorImport)
