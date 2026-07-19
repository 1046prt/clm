from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ai_analysis.models import AnalysisResult, RiskFlag


@login_required
def analysis_detail(request, pk):
    analysis = AnalysisResult.objects.select_related("contract").prefetch_related(
        "risk_flags", "metadata"
    ).get(pk=pk)

    context = {
        "analysis": analysis,
        "metadata": getattr(analysis, "metadata", None),
        "risk_flags": analysis.risk_flags.all(),
    }
    return render(request, "ai_analysis/detail.html", context)


@login_required
def mark_risk_reviewed(request, pk):
    if request.method == "POST":
        risk = RiskFlag.objects.get(pk=pk)
        risk.is_reviewed = True
        risk.reviewed_by = request.user
        risk.review_notes = request.POST.get("notes", "")
        risk.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)
