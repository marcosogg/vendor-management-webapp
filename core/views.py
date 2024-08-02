from django.http import JsonResponse
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.db.models import Sum, Count, Q, Avg
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from .models import Vendor, Part, Spend, Risk, Activity
from .forms import VendorForm
from .utils import (
    log_error,
    format_currency,
    get_relevant_news,
)
from django.views.generic import DetailView
from django.db.models.functions import Rank
from django.utils import timezone
from django.db.models import Sum

import logging

logger = logging.getLogger(__name__)


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_vendors"] = Vendor.objects.count()
        total_spend = Spend.objects.aggregate(total=Sum("usd_amount"))["total"] or 0
        context["total_spend"] = format_currency(total_spend)
        context["high_risk_vendors"] = Vendor.objects.filter(
            risk__risk_level="HIGH"
        ).count()
        context["recent_activities"] = Activity.objects.all().order_by("-date")[:5]

        news_articles = get_relevant_news()
        logger.info(f"Fetched {len(news_articles)} articles for the home page")
        context["news_articles"] = news_articles

        return context


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

        # Calculate rank by spend for the past 4 years
        current_year = timezone.now().year
        rank_data = []
        for year in range(current_year - 3, current_year + 1):
            # Get all spends for the year
            year_spends = (
                Spend.objects.filter(year=year)
                .values("vendor")
                .annotate(total_spend=Sum("usd_amount"))
                .order_by("-total_spend")
            )

            # Calculate ranks
            spend_dict = {item["vendor"]: item["total_spend"] for item in year_spends}
            sorted_vendors = sorted(spend_dict, key=spend_dict.get, reverse=True)
            ranks = {
                vendor_id: rank + 1 for rank, vendor_id in enumerate(sorted_vendors)
            }

            # Get this vendor's rank and spend
            vendor_spend = spend_dict.get(vendor.id, 0)
            vendor_rank = ranks.get(vendor.id, None)

            rank_data.append(
                {
                    "year": year,
                    "rank": vendor_rank,
                    "total_vendors": len(year_spends),
                    "spend": vendor_spend,
                }
            )

        context["rank_data"] = rank_data

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


def risk_distribution(request):
    risk_data = Risk.objects.values("risk_level").annotate(count=Count("risk_level"))
    return JsonResponse(list(risk_data), safe=False)
