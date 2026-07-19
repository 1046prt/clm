from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Obligation, RenewalAlert
from contracts.models import Contract


@login_required
def obligation_dashboard(request):
    today = timezone.now().date()

    overdue = Obligation.objects.filter(
        status__in=["pending", "in_progress"],
        due_date__lt=today,
    ).select_related("contract", "assigned_to", "responsible_party")

    upcoming = Obligation.objects.filter(
        status__in=["pending", "in_progress"],
        due_date__gte=today,
        due_date__lte=today + timezone.timedelta(days=30),
    ).select_related("contract", "assigned_to", "responsible_party")

    all_obligations = Obligation.objects.select_related(
        "contract", "assigned_to", "category"
    ).order_by("due_date")[:50]

    expiring_contracts = Contract.objects.filter(
        expiry_date__gte=today,
        expiry_date__lte=today + timezone.timedelta(days=90),
        status="active",
    )

    alerts = RenewalAlert.objects.filter(
        is_dismissed=False
    ).select_related("contract")[:20]

    context = {
        "overdue_obligations": overdue,
        "upcoming_obligations": upcoming,
        "all_obligations": all_obligations,
        "expiring_contracts": expiring_contracts,
        "alerts": alerts,
        "today": today,
    }
    return render(request, "obligations/dashboard.html", context)


@login_required
def obligation_list(request):
    obligations = Obligation.objects.select_related(
        "contract", "assigned_to", "responsible_party", "category"
    ).order_by("due_date")
    return render(request, "obligations/list.html", {"obligations": obligations})


@login_required
def dismiss_alert(request, pk):
    if request.method == "POST":
        alert = get_object_or_404(RenewalAlert, pk=pk)
        alert.is_dismissed = True
        alert.save()
        messages.success(request, "Alert dismissed.")
    return redirect("obligations:dashboard")
