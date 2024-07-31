from django.urls import path
from .views import (
    DashboardView,
    VendorListView,
    VendorProfileView,
    global_search,
    dashboard_data,
)

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("api/dashboard-data/", dashboard_data, name="dashboard_data"),
    path("vendors/", VendorListView.as_view(), name="vendor_list"),
    path("vendors/<int:pk>/", VendorProfileView.as_view(), name="vendor_profile"),
    path("search/", global_search, name="global_search"),
]
