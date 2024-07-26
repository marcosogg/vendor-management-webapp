from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Vendor, Part, Spend, Risk
from .forms import VendorForm, PartForm, SpendForm, RiskForm

def home(request):
    return render(request, 'core/home.html')

class VendorListView(ListView):
    model = Vendor
    template_name = 'core/vendor_list.html'
    context_object_name = 'vendors'
    paginate_by = 10

class VendorDetailView(DetailView):
    model = Vendor
    template_name = 'core/vendor_profile.html'
    context_object_name = 'vendor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.get_object()
        context['parts'] = vendor.parts.all()
        context['spends'] = vendor.spends.all()
        context['risk'] = vendor.risk
        return context

class VendorCreateView(CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'core/vendor_form.html'
    success_url = reverse_lazy('vendor-list')

class VendorUpdateView(UpdateView):
    model = Vendor
    form_class = VendorForm
    template_name = 'core/vendor_form.html'
    success_url = reverse_lazy('vendor-list')

class PartCreateView(CreateView):
    model = Part
    form_class = PartForm
    template_name = 'core/part_form.html'
    success_url = reverse_lazy('vendor-list')

class SpendCreateView(CreateView):
    model = Spend
    form_class = SpendForm
    template_name = 'core/spend_form.html'
    success_url = reverse_lazy('vendor-list')

class RiskCreateView(CreateView):
    model = Risk
    form_class = RiskForm
    template_name = 'core/risk_form.html'
    success_url = reverse_lazy('vendor-list')
