from django.urls import path
from .views import DashboardView, dashboard_data

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("api/dashboard-data/", dashboard_data, name="dashboard_data"),
]
