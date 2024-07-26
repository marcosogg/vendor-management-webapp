# core/admin.py

from django.contrib import admin
from .models import Supplier, Part, Spend, Risk

admin.site.register(Supplier)
admin.site.register(Part)
admin.site.register(Spend)
admin.site.register(Risk)
