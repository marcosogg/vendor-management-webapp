# core/urls.py

from django.urls import path
from .views import HomeView, VendorListView, VendorDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('vendors/', VendorListView.as_view(), name='vendor_list'),
    path('vendors/<int:pk>/', VendorDetailView.as_view(), name='vendor_detail'),
]
