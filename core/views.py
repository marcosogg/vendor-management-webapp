from django.http import JsonResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.db.models import Sum, Count, Q, Avg
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.contrib import messages
from .models import Vendor, Part, Spend, Risk, Activity
from .forms import VendorForm
from .utils import log_error

import logging
import math

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    @log_error
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Total vendors and parts
        context["total_vendors"] = Vendor.objects.count()
        context["total_parts"] = Part.objects.count()

        # Total spend
        total_spend = Spend.objects.aggregate(total=Sum("usd_amount"))["total"] or 0
        context["total_spend"] = self.format_currency(total_spend)

        # Average risk score
        avg_risk_score = (
            Risk.objects.aggregate(Avg("total_score"))["total_score__avg"] or 0
        )
        context["avg_risk_score"] = round(avg_risk_score, 2)

        # High risk vendors
        context["high_risk_vendors"] = Vendor.objects.filter(
            risk__risk_level="HIGH"
        ).count()

        # Top vendors by spend
        context["top_vendors"] = Vendor.objects.annotate(
            total_spend=Sum("spends__usd_amount")
        ).order_by("-total_spend")[:5]

        # Recent activities
        context["recent_activities"] = Activity.objects.all().order_by("-date")[:10]

        return context

    def format_currency(self, amount):
        if amount >= 1_000_000_000:
            return f"${amount / 1_000_000_000:.2f}B"
        elif amount >= 1_000_000:
            return f"${amount / 1_000_000:.2f}M"
        elif amount >= 1_000:
            return f"${amount / 1_000:.2f}K"
        else:
            return f"${amount:,.2f}"


class VendorListView(LoginRequiredMixin, ListView):
    model = Vendor
    template_name = "core/vendor_list.html"
    context_object_name = "vendors"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related("risk")

        sort_by = self.request.GET.get("sort_by", "vendor_name")
        sort_order = self.request.GET.get("sort_order", "asc")
        if sort_order == "desc":
            sort_by = f"-{sort_by}"
        queryset = queryset.order_by(sort_by)

        search_query = self.request.GET.get("search", "")
        relationship_type = self.request.GET.get("relationship_type", "")
        risk_level = self.request.GET.get("risk_level", "")

        if search_query:
            queryset = queryset.filter(
                Q(vendor_name__icontains=search_query)
                | Q(vendor_id__icontains=search_query)
            )

        if relationship_type:
            queryset = queryset.filter(relationship_type=relationship_type)

        if risk_level:
            queryset = queryset.filter(risk__risk_level=risk_level)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["relationship_type"] = self.request.GET.get("relationship_type", "")
        context["risk_level"] = self.request.GET.get("risk_level", "")
        context["sort_by"] = self.request.GET.get("sort_by", "vendor_name")
        context["sort_order"] = self.request.GET.get("sort_order", "asc")
        context["vendor_relationship_types"] = Vendor._meta.get_field(
            "relationship_type"
        ).choices
        context["risk_levels"] = Risk._meta.get_field("risk_level").choices
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

        avg_discount = vendor.parts.aggregate(Avg("discount"))["discount__avg"]
        context["avg_discount"] = (
            round(avg_discount, 2) if avg_discount is not None else 0
        )

        context["risk"] = vendor.risk

        if vendor.risk.risk_level == "HIGH":
            messages.warning(
                self.request,
                f"Warning: {vendor.vendor_name} is classified as a high-risk vendor.",
            )

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


def global_search(request):
    query = request.GET.get("q")
    results = []
    if query:
        vendor_results = Vendor.objects.filter(
            Q(vendor_name__icontains=query) | Q(vendor_id__icontains=query)
        )
        part_results = Part.objects.filter(part_number__icontains=query)
        spend_results = Spend.objects.filter(vendor__vendor_name__icontains=query)

        for vendor in vendor_results:
            results.append(
                {
                    "type": "Vendor",
                    "title": vendor.vendor_name,
                    "description": f"Vendor ID: {vendor.vendor_id}",
                    "url": reverse("vendor_profile", kwargs={"pk": vendor.pk}),
                }
            )

        for part in part_results:
            results.append(
                {
                    "type": "Part",
                    "title": part.part_number,
                    "description": f"Vendor: {part.vendor.vendor_name}",
                    "url": reverse("vendor_profile", kwargs={"pk": part.vendor.pk}),
                }
            )

        for spend in spend_results:
            results.append(
                {
                    "type": "Spend",
                    "title": f"Spend for {spend.vendor.vendor_name}",
                    "description": f"Year: {spend.year}, Amount: ${spend.usd_amount:,.2f}",
                    "url": reverse("vendor_profile", kwargs={"pk": spend.vendor.pk}),
                }
            )

    return render(
        request, "core/search_results.html", {"query": query, "results": results}
    )


def vendor_performance(request):
    performance_data = Vendor.objects.annotate(
        avg_rating=Avg("rating"), avg_discount=Avg("average_discount")
    ).values("avg_rating", "avg_discount")
    return JsonResponse(list(performance_data), safe=False)


def contract_type_distribution(request):
    contract_data = Vendor.objects.values("contract_type").annotate(
        count=Count("contract_type")
    )
    return JsonResponse(list(contract_data), safe=False)


def format_currency(amount):
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.2f}K"
    else:
        return f"${amount:,.2f}"


def dashboard_data(request):
    try:
        # Fetch and calculate all required data
        risk_distribution = list(
            Risk.objects.values("risk_level").annotate(count=Count("risk_level"))
        )

        spend_by_year = list(
            Spend.objects.values("year").annotate(total_spend=Sum("usd_amount"))
        )
        total_spend = sum(
            item["total_spend"] for item in spend_by_year if item["total_spend"]
        )

        spend_by_relationship = list(
            Spend.objects.values("relationship_type").annotate(
                total_spend=Sum("usd_amount")
            )
        )

        vendor_performance = Vendor.objects.aggregate(
            avg_rating=Avg("rating"), avg_discount=Avg("average_discount")
        )

        contract_distribution = list(
            Vendor.objects.values("contract_type").annotate(
                count=Count("contract_type")
            )
        )

        geographical_distribution = list(
            Vendor.objects.values("country").annotate(count=Count("country"))
        )

        high_risk_vendors = Vendor.objects.filter(risk__risk_level="HIGH").count()

        data = {
            "risk_distribution": list(
                Risk.objects.values("risk_level").annotate(count=Count("risk_level"))
            ),
            "total_spend": format_currency(total_spend),
            "spend_by_year": list(
                Spend.objects.values("year").annotate(total_spend=Sum("usd_amount"))
            ),
            "spend_by_relationship": list(
                Spend.objects.values("relationship_type").annotate(
                    total_spend=Sum("usd_amount")
                )
            ),
            "vendor_performance": Vendor.objects.aggregate(
                avg_rating=Avg("rating"), avg_discount=Avg("average_discount")
            ),
            "contract_distribution": list(
                Vendor.objects.values("contract_type").annotate(
                    count=Count("contract_type")
                )
            ),
            "geographical_distribution": list(
                Vendor.objects.values("country").annotate(count=Count("country"))
            ),
            "high_risk_vendors": Vendor.objects.filter(risk__risk_level="HIGH").count(),
        }
        logger.info(f"Dashboard data: {data}")
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {str(e)}")
        return JsonResponse(
            {"error": "An error occurred while fetching dashboard data"}, status=500
        )


def dashboard(request):
    context = {
        "total_vendors": Vendor.objects.count(),
        "total_spend": Spend.objects.aggregate(total=Sum("usd_amount"))["total"],
        "avg_risk_score": Risk.objects.aggregate(avg_score=Avg("total_score"))[
            "avg_score"
        ],
        "recent_activities": Activity.objects.all().order_by("-date")[:10],
    }
    return render(request, "core/dashboard.html", context)


def risk_distribution(request):
    risk_data = Risk.objects.values("risk_level").annotate(count=Count("risk_level"))
    return JsonResponse(list(risk_data), safe=False)
