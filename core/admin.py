# core/admin.py
from django.contrib import admin
from .models import Vendor, Part, Spend, Risk

admin.site.register(Vendor)
admin.site.register(Part)
admin.site.register(Spend)
admin.site.register(Risk)
