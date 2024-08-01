from django.urls import path
from .views import (
    VendorListView,
    VendorProfileView,
    global_search,
)

urlpatterns = [
    path("", VendorListView.as_view(), name="vendor_list"),
    path("<int:pk>/", VendorProfileView.as_view(), name="vendor_profile"),
    path("search/", global_search, name="global_search"),
]
