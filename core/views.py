# core/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')

def dashboard(request):
    return render(request, 'core/dashboard.html')

def vendor_list(request):
    return render(request, 'core/vendor_list.html')

def vendor_profile(request, vendor_id):
    return render(request, 'core/vendor_profile.html', {'vendor_id': vendor_id})
