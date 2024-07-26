# data_import/views.py
from django.shortcuts import render

def import_data(request):
    return render(request, 'data_import/import.html')
