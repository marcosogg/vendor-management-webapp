# data_import/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.import_data, name='import_data'),
]
