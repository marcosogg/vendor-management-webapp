"""
URL configuration for vendor_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# core/models.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView  # Import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),  # Use HomeView for root URL
    path("dashboard/", include("dashboard.urls")),
    path("vendors/", include("core.urls")),  # Keep this for vendor-related URLs
    path("import/", include("data_import.urls")),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
