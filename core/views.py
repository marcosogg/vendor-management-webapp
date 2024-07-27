from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.db.models import Sum, Count, Q
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from django.core.exceptions import ValidationError

from .models import Vendor, Part, Spend, Risk
from .forms import VendorForm
from .utils import log_error

import logging

logger = logging.getLogger(__name__)

@method_decorator(login_required, name="dispatch")
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    # @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @log_error
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_vendors"] = Vendor.objects.count()
        context["total_parts"] = Part.objects.count()
        context["total_spend"] = (
            Spend.objects.aggregate(Sum("usd_amount"))["usd_amount__sum"] or 0
        )
        context["high_risk_vendors"] = Vendor.objects.filter(
            risk__risk_level="HIGH"
        ).count()
        context["top_vendors"] = Vendor.objects.annotate(
            total_spend=Sum("spends__usd_amount")
        ).order_by("-total_spend")[:5]
        return context

@method_decorator(login_required, name="dispatch")
class VendorListView(ListView):
    model = Vendor
    template_name = "core/vendor_list.html"
    context_object_name = "vendors"
    paginate_by = 10

    def get_queryset(self):
        try:
            queryset = super().get_queryset().select_related("risk")
            search_query = escape(self.request.GET.get("search", ""))
            relationship_type = escape(self.request.GET.get("relationship_type", ""))
            risk_level = escape(self.request.GET.get("risk_level", ""))

            if search_query:
                queryset = queryset.filter(
                    Q(vendor_name__icontains=search_query) |
                    Q(vendor_id__icontains=search_query)
                )

            if relationship_type:
                queryset = queryset.filter(relationship_type=relationship_type)

            if risk_level:
                queryset = queryset.filter(risk__risk_level=risk_level)

            logger.debug(f"Vendor query: {queryset.query}")
            return queryset
        except ValidationError as e:
            logger.error(f"Validation error in VendorListView: {e}")
            return Vendor.objects.none()
        except Exception as e:
            logger.error(f"Unexpected error in VendorListView: {e}")
            return Vendor.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["relationship_type"] = self.request.GET.get("relationship_type", "")
        context["risk_level"] = self.request.GET.get("risk_level", "")
        context["vendor_relationship_types"] = Vendor._meta.get_field('relationship_type').choices
        context["risk_levels"] = Risk._meta.get_field('risk_level').choices
        return context

@method_decorator(login_required, name="dispatch")
class VendorProfileView(LoginRequiredMixin, DetailView):
    model = Vendor
    template_name = "core/vendor_profile.html"
    context_object_name = "vendor"

    @log_error
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("parts", "spends")
            .select_related("risk")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = self.object
        context["parts"] = vendor.parts.all()
        context["spends"] = vendor.spends.all().order_by("-year")
        context["risk"] = vendor.risk
        return context

@method_decorator(login_required, name="dispatch")
class VendorCreateView(LoginRequiredMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = "core/vendor_form.html"
    success_url = reverse_lazy("vendor_list")

    @log_error
    def form_valid(self, form):
        response = super().form_valid(form)
        Risk.objects.create(vendor=self.object, risk_level="LOW")
        return response

@method_decorator(login_required, name="dispatch")
class VendorUpdateView(LoginRequiredMixin, UpdateView):
    model = Vendor
    form_class = VendorForm
    template_name = "core/vendor_form.html"
    success_url = reverse_lazy("vendor_list")

    @log_error
    def form_valid(self, form):
        return super().form_valid(form)

# You can add more views here as needed, such as views for Part, Spend, and Risk models
