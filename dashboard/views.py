from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg
from core.models import Vendor, Part, Spend, Risk, Activity
from core.utils import log_error
from core.views import format_currency  # Import the existing format_currency function


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"

    @log_error
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_vendors"] = Vendor.objects.count()
        context["total_parts"] = Part.objects.count()
        total_spend = Spend.objects.aggregate(total=Sum("usd_amount"))["total"] or 0
        context["total_spend"] = format_currency(
            total_spend
        )  # Use the imported function
        avg_risk_score = (
            Risk.objects.aggregate(Avg("total_score"))["total_score__avg"] or 0
        )
        context["avg_risk_score"] = round(avg_risk_score, 2)
        context["high_risk_vendors"] = Vendor.objects.filter(
            risk__risk_level="HIGH"
        ).count()
        context["top_vendors"] = Vendor.objects.annotate(
            total_spend=Sum("spends__usd_amount")
        ).order_by("-total_spend")[:5]
        context["recent_activities"] = Activity.objects.all().order_by("-date")[:10]
        return context


def dashboard_data(request):
    try:
        total_spend = Spend.objects.aggregate(total=Sum("usd_amount"))["total"] or 0
        data = {
            "risk_distribution": list(
                Risk.objects.values("risk_level").annotate(count=Count("risk_level"))
            ),
            "total_spend": format_currency(total_spend),  # Use the imported function
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
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse(
            {"error": "An error occurred while fetching dashboard data"}, status=500
        )
