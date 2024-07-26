# core/views.py

from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.db.models import Q, Sum, Count
from .models import Vendor, Part, Spend, Risk


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vendor_count"] = Vendor.objects.count()
        context["part_count"] = Part.objects.count()
        context["spend_total"] = (
            Spend.objects.aggregate(total=Sum("usd_amount"))["total"] or 0
        )
        context["high_risk_count"] = Risk.objects.filter(risk_level="High").count()

        # Additional statistics
        context["avg_spend_per_vendor"] = (
            context["spend_total"] / context["vendor_count"]
            if context["vendor_count"] > 0
            else 0
        )
        context["top_vendors"] = Vendor.objects.annotate(
            total_spend=Sum("spends__usd_amount")
        ).order_by("-total_spend")[:5]

        return context


class VendorListView(ListView):
    model = Vendor
    template_name = "vendor_list.html"
    context_object_name = "vendors"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.filter(
                Q(vendor_name__icontains=search_query)
                | Q(vendor_id__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


class VendorDetailView(DetailView):
    model = Vendor
    template_name = "vendor_detail.html"
    context_object_name = "vendor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.get_object()
        context["parts"] = vendor.parts.all()
        context["spends"] = vendor.spends.all()
        context["risk"] = vendor.risk
        return context


# Remove any other views that were used for data modification
