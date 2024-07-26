from django.urls import path
from .views import (
    home,
    VendorListView,
    VendorDetailView,
    VendorCreateView,
    VendorUpdateView,
    PartCreateView,
    SpendCreateView,
    RiskCreateView,
)

urlpatterns = [
    path("", home, name="home"),
    path("vendors/", VendorListView.as_view(), name="vendor-list"),
    path("vendors/<int:pk>/", VendorDetailView.as_view(), name="vendor-detail"),
    path("vendors/add/", VendorCreateView.as_view(), name="vendor-create"),
    path("vendors/<int:pk>/edit/", VendorUpdateView.as_view(), name="vendor-update"),
    path("parts/add/", PartCreateView.as_view(), name="part-create"),
    path("spends/add/", SpendCreateView.as_view(), name="spend-create"),
    path("risks/add/", RiskCreateView.as_view(), name="risk-create"),
]
