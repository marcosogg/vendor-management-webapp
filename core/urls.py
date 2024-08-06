from django.urls import path, include
from .views import (
    VendorListView,
    VendorProfileView,
    global_search,
    VendorViewSet,
    PartViewSet,
    SpendViewSet,
    RiskViewSet,
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"vendors", VendorViewSet)
router.register(r"parts", PartViewSet)
router.register(r"spend", SpendViewSet)
router.register(r"risk", RiskViewSet)

urlpatterns = [
    path("", VendorListView.as_view(), name="vendor_list"),
    path("<int:pk>/", VendorProfileView.as_view(), name="vendor_profile"),
    path("search/", global_search, name="global_search"),
]
