from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, F
from core.models import Vendor, Part, Spend, Risk, Activity
from core.utils import log_error, format_currency
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models.functions import TruncYear
import logging

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    @log_error
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_vendors"] = Vendor.objects.count()
        context["total_parts"] = Part.objects.count()
        total_spend = Spend.objects.aggregate(total=Sum("usd_amount"))["total"] or 0
        context["total_spend"] = format_currency(total_spend)
        avg_risk_score = (
            Risk.objects.aggregate(avg_score=Avg("total_score"))["avg_score"] or 0
        )
        context["avg_risk_score"] = round(avg_risk_score, 2)
        context["high_risk_vendors"] = Risk.objects.filter(risk_level="HIGH").count()
        context["top_vendors"] = Vendor.objects.annotate(
            total_spend=Sum("spends__usd_amount")
        ).order_by("-total_spend")[:5]
        context["recent_activities"] = Activity.objects.all().order_by("-date")[:10]
        return context


@log_error
def dashboard_data(request):
    try:
        date_range = request.GET.get("date_range", "1")
        sort_relationship = request.GET.get("sort_relationship", "total")

        end_date = timezone.now().date()
        if date_range == "1":
            start_date = end_date - relativedelta(years=1)
        elif date_range == "3":
            start_date = end_date - relativedelta(years=3)
        else:
            start_date = None

        spend_query = Spend.objects.all()
        if start_date:
            spend_query = spend_query.filter(year__gte=start_date.year)

        total_spend = spend_query.aggregate(total=Sum("usd_amount"))["total"] or 0

        risk_distribution = list(
            Risk.objects.values("risk_level")
            .annotate(count=Count("risk_level"))
            .order_by("risk_level")
        )

        spend_by_year = list(
            spend_query.values("year")
            .annotate(total_spend=Sum("usd_amount"))
            .order_by("year")
        )

        spend_by_relationship = list(
            spend_query.values("relationship_type").annotate(
                total_spend=Sum("usd_amount")
            )
        )

        if sort_relationship == "alphabetical":
            spend_by_relationship.sort(key=lambda x: x["relationship_type"])
        else:
            spend_by_relationship.sort(key=lambda x: x["total_spend"], reverse=True)

        contract_distribution = list(
            Vendor.objects.values("contract_type")
            .annotate(count=Count("contract_type"))
            .order_by("-count")
        )

        geographical_distribution = list(
            Vendor.objects.exclude(country__isnull=True)
            .exclude(country__exact="")
            .values("country")
            .annotate(count=Count("country"))
            .order_by("-count")
        )

        vendor_performance = Vendor.objects.aggregate(
            avg_rating=Avg("rating"), avg_discount=Avg("average_discount")
        )

        avg_risk_score = (
            Risk.objects.aggregate(avg_score=Avg("total_score"))["avg_score"] or 0
        )

        data = {
            "risk_distribution": risk_distribution,
            "total_spend": format_currency(total_spend),
            "spend_by_year": spend_by_year,
            "spend_by_relationship": spend_by_relationship,
            "vendor_performance": vendor_performance,
            "contract_distribution": contract_distribution,
            "geographical_distribution": {
                item["country"]: item["count"] for item in geographical_distribution
            },
            "high_risk_vendors": Risk.objects.filter(risk_level="HIGH").count(),
            "total_vendors": Vendor.objects.count(),
            "total_parts": Part.objects.count(),
            "avg_risk_score": round(avg_risk_score, 2),
        }
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error in dashboard_data: {str(e)}", exc_info=True)
        return JsonResponse(
            {"error": f"An error occurred while fetching dashboard data: {str(e)}"},
            status=500,
        )
