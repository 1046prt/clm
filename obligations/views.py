from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Obligation, RenewalAlert
from .forms import ObligationForm, ObligationCreateForm
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
    obligations = Paginator(
        Obligation.objects.select_related("contract", "assigned_to", "responsible_party", "category").order_by("due_date"),
        50
    ).get_page(request.GET.get("page"))
    return render(request, "obligations/list.html", {"obligations": obligations, "page_obj": obligations})


@login_required
def dismiss_alert(request, pk):
    if request.method == "POST":
        alert = get_object_or_404(RenewalAlert, pk=pk)
        alert.is_dismissed = True
        alert.save()
        messages.success(request, "Alert dismissed.")
    return redirect("obligations:dashboard")


# ── Obligation CRUD ──────────────────────────

@login_required
def obligation_create(request):
    if request.method == "POST":
        form = ObligationCreateForm(request.POST)
        if form.is_valid():
            obligation = form.save()
            messages.success(request, f"Obligation '{obligation.title}' created.")
            return redirect("obligations:list")
    else:
        form = ObligationCreateForm()
    return render(request, "obligations/obligation_form.html", {"form": form, "action": "Create"})


@login_required
def obligation_edit(request, pk):
    obligation = get_object_or_404(Obligation, pk=pk)
    if request.method == "POST":
        form = ObligationForm(request.POST, instance=obligation)
        if form.is_valid():
            form.save()
            messages.success(request, f"Obligation '{obligation.title}' updated.")
            return redirect("obligations:list")
    else:
        form = ObligationForm(instance=obligation)
    return render(request, "obligations/obligation_form.html", {"form": form, "action": "Edit"})


@login_required
def obligation_complete(request, pk):
    obligation = get_object_or_404(Obligation, pk=pk)
    if request.method == "POST":
        obligation.status = "completed"
        obligation.completed_date = timezone.now().date()
        obligation.save()
        messages.success(request, f"Obligation '{obligation.title}' marked as completed.")
    return redirect("obligations:list")


@login_required
def obligation_delete(request, pk):
    obligation = get_object_or_404(Obligation, pk=pk)
    if request.method == "POST":
        title = obligation.title
        obligation.delete()
        messages.success(request, f"Obligation '{title}' deleted.")
        return redirect("obligations:list")
    return render(request, "contracts/confirm_delete.html", {"object": obligation, "object_type": "Obligation"})
