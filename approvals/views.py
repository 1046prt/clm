from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import ApprovalRequest, ApprovalAction
from .forms import ApprovalActionForm, InitiateApprovalForm
from .engine import initiate_approval, process_approval
from contracts.models import Contract


@login_required
def approval_list(request):
    tab = request.GET.get("tab", "pending")
    user = request.user

    if tab == "my_requests":
        approvals = ApprovalRequest.objects.filter(
            requested_by=user
        ).select_related("contract", "chain", "current_step")
    elif tab == "pending":
        approvals = ApprovalRequest.objects.filter(
            current_step__approver=user,
            status="in_progress",
        ).select_related("contract", "chain", "current_step")
    elif tab == "approved":
        approvals = ApprovalRequest.objects.filter(status="approved").select_related("contract", "chain")
    elif tab == "rejected":
        approvals = ApprovalRequest.objects.filter(status="rejected").select_related("contract", "chain")
    else:
        approvals = ApprovalRequest.objects.all().select_related("contract", "chain")

    context = {
        "approvals": approvals,
        "active_tab": tab,
    }
    return render(request, "approvals/list.html", context)


@login_required
def approval_detail(request, pk):
    approval = get_object_or_404(
        ApprovalRequest.objects.select_related(
            "contract", "chain", "current_step", "requested_by"
        ).prefetch_related("action_logs__actor", "action_logs__step", "chain__steps"),
        pk=pk,
    )

    action_form = ApprovalActionForm()
    is_current_approver = (
        approval.status == "in_progress"
        and approval.current_step
        and approval.current_step.approver == request.user
    )

    context = {
        "approval": approval,
        "action_form": action_form,
        "is_current_approver": is_current_approver,
        "action_logs": approval.action_logs.all(),
        "steps": approval.chain.steps.order_by("step_number") if approval.chain else [],
    }
    return render(request, "approvals/detail.html", context)


@login_required
def initiate_approval_view(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    if request.method == "POST":
        form = InitiateApprovalForm(request.POST)
        if form.is_valid():
            approval = initiate_approval(
                contract,
                request.user,
                notes=form.cleaned_data.get("notes", ""),
            )
            if approval:
                messages.success(request, "Approval process initiated.")
            else:
                messages.warning(request, "No matching approval chain found.")
            return redirect("approvals:detail", pk=approval.pk if approval else pk)
    else:
        form = InitiateApprovalForm()

    return render(request, "approvals/initiate.html", {
        "form": form,
        "contract": contract,
    })


@login_required
def process_approval_view(request, pk):
    approval = get_object_or_404(ApprovalRequest, pk=pk)

    if not approval.current_step or approval.current_step.approver != request.user:
        messages.error(request, "You are not authorized to act on this approval.")
        return redirect("approvals:detail", pk=pk)

    if request.method == "POST":
        form = ApprovalActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data["action"]
            comment = form.cleaned_data.get("comment", "")

            process_approval(
                approval,
                approval.current_step,
                request.user,
                action,
                comment,
            )

            action_display = action.replace("_", " ")
            messages.success(request, f"Action '{action_display}' recorded successfully.")
            return redirect("approvals:detail", pk=pk)

    return redirect("approvals:detail", pk=pk)
