from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import JsonResponse

from .models import Contract, Party, ContractCategory, ContractComment, ContractVersion
from .forms import ContractForm, ContractUploadForm, ContractSearchForm, ContractCommentForm
from ai_analysis.extractor import analyze_contract, extract_text_from_file
from ai_analysis.risk_detector import detect_risks


@login_required
def dashboard(request):
    today = timezone.now().date()
    contracts = Contract.objects.all()

    total_contracts = contracts.count()
    active_contracts = contracts.filter(status="active").count()
    pending_approvals = contracts.filter(status="pending_approval").count()
    expired_contracts = contracts.filter(
        expiry_date__lt=today, status__in=["active", "approved"]
    ).count()

    expiring_soon = contracts.filter(
        expiry_date__gte=today,
        expiry_date__lte=today + timezone.timedelta(days=30),
        status="active",
    )[:10]

    recent_contracts = contracts.order_by("-created_at")[:10]

    status_distribution = contracts.values("status").annotate(count=Count("id"))
    category_distribution = contracts.values("category__name").annotate(count=Count("id")).filter(category__name__isnull=False)

    total_value = contracts.filter(status="active").aggregate(total=Sum("total_value"))["total"] or 0

    context = {
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "pending_approvals": pending_approvals,
        "expired_contracts": expired_contracts,
        "expiring_soon": expiring_soon,
        "recent_contracts": recent_contracts,
        "status_distribution": list(status_distribution),
        "category_distribution": list(category_distribution),
        "total_value": total_value,
    }
    return render(request, "dashboard.html", context)


@login_required
def contract_list(request):
    form = ContractSearchForm(request.GET)
    contracts = Contract.objects.select_related("category", "internal_owner").prefetch_related("parties")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        status = form.cleaned_data.get("status")
        category = form.cleaned_data.get("category")
        priority = form.cleaned_data.get("priority")

        if q:
            contracts = contracts.filter(
                Q(title__icontains=q) |
                Q(contract_number__icontains=q) |
                Q(description__icontains=q) |
                Q(parties__name__icontains=q)
            ).distinct()
        if status:
            contracts = contracts.filter(status=status)
        if category:
            contracts = contracts.filter(category=category)
        if priority:
            contracts = contracts.filter(priority=priority)

    context = {
        "contracts": contracts,
        "search_form": form,
    }
    return render(request, "contracts/list.html", context)


@login_required
def contract_detail(request, pk):
    contract = get_object_or_404(
        Contract.objects.select_related("category", "template", "internal_owner", "created_by")
        .prefetch_related("parties", "comments__author", "versions", "approval_requests__chain",
                          "obligations", "analysis_results__risk_flags", "signature_requests"),
        pk=pk,
    )
    comment_form = ContractCommentForm()

    context = {
        "contract": contract,
        "comment_form": comment_form,
        "versions": contract.versions.all()[:10],
        "comments": contract.comments.all(),
        "approval_requests": contract.approval_requests.all()[:5],
        "obligations": contract.obligations.all()[:10],
        "analysis_results": contract.analysis_results.all()[:5],
        "risk_flags": contract.analysis_results.filter(risk_flags__isnull=False).values_list(
            "risk_flags", flat=True
        ),
        "signature_requests": contract.signature_requests.all()[:5],
    }
    return render(request, "contracts/detail.html", context)


@login_required
def contract_create(request):
    if request.method == "POST":
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.created_by = request.user
            contract.internal_owner = request.user
            contract.save()
            form.save_m2m()
            messages.success(request, f"Contract '{contract.title}' created successfully.")
            return redirect(contract.get_absolute_url())
    else:
        form = ContractForm()

    return render(request, "contracts/create.html", {"form": form, "action": "Create"})


@login_required
def contract_edit(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == "POST":
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            old_version = contract.version
            contract = form.save()

            ContractVersion.objects.create(
                contract=contract,
                version_number=old_version,
                content=contract.content,
                changes_summary=f"Edited by {request.user.username}",
                created_by=request.user,
            )

            messages.success(request, f"Contract '{contract.title}' updated successfully.")
            return redirect(contract.get_absolute_url())
    else:
        form = ContractForm(instance=contract)

    return render(request, "contracts/create.html", {"form": form, "contract": contract, "action": "Edit"})


@login_required
def contract_upload(request):
    if request.method == "POST":
        form = ContractUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            contract = Contract.objects.create(
                title=form.cleaned_data["title"],
                description=form.cleaned_data.get("description", ""),
                category=form.cleaned_data.get("category"),
                uploaded_file=uploaded_file,
                created_by=request.user,
                internal_owner=request.user,
                status="draft",
            )

            text = extract_text_from_file(contract)
            if text:
                contract.content = text[:50000]
                contract.save()

            messages.success(request, f"Contract '{contract.title}' uploaded and text extracted.")
            return redirect(contract.get_absolute_url())
    else:
        form = ContractUploadForm()

    return render(request, "contracts/upload.html", {"form": form})


@login_required
def contract_add_comment(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == "POST":
        form = ContractCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.contract = contract
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
    return redirect("contracts:detail", pk=pk)


@login_required
def contract_delete(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == "POST":
        title = contract.title
        contract.delete()
        messages.success(request, f"Contract '{title}' deleted.")
        return redirect("contracts:list")
    return render(request, "contracts/confirm_delete.html", {"contract": contract})


@login_required
def run_analysis(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == "POST":
        analysis = analyze_contract(contract, request.user)
        if analysis.status == "completed":
            detect_risks(analysis, request.user)
            messages.success(request, "AI analysis completed. Risk flags have been generated.")
        else:
            messages.error(request, f"Analysis failed: {analysis.error_message}")
    return redirect("contracts:detail", pk=pk)
