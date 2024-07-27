from django.urls import path
from .views import DashboardView, VendorListView, VendorProfileView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("vendors/", VendorListView.as_view(), name="vendor_list"),
    path("vendors/<int:pk>/", VendorProfileView.as_view(), name="vendor_profile"),
]
