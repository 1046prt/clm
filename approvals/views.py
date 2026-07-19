from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import ApprovalChain, ApprovalRequest, ApprovalAction
from .forms import ApprovalChainForm, ApprovalStepFormSet, ApprovalActionForm, InitiateApprovalForm
from .engine import initiate_approval, process_approval
from contracts.models import Contract


# ── Approval Requests ────────────────────────

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


# ── Approval Chain CRUD ──────────────────────

@login_required
def chain_list(request):
    chains = ApprovalChain.objects.prefetch_related("steps").all()
    return render(request, "approvals/chain_list.html", {"chains": chains})


@login_required
def chain_detail(request, pk):
    chain = get_object_or_404(
        ApprovalChain.objects.prefetch_related("steps__approver"),
        pk=pk,
    )
    return render(request, "approvals/chain_detail.html", {"chain": chain})


@login_required
def chain_create(request):
    if request.method == "POST":
        form = ApprovalChainForm(request.POST)
        formset = ApprovalStepFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            chain = form.save()
            steps = formset.save(commit=False)
            for step in steps:
                step.chain = chain
                step.save()
            for step in formset.deleted_objects:
                step.delete()
            messages.success(request, f"Approval chain '{chain.name}' created.")
            return redirect("approvals:chain_list")
    else:
        form = ApprovalChainForm()
        formset = ApprovalStepFormSet(queryset=ApprovalStep.objects.none())
    return render(request, "approvals/chain_form.html", {"form": form, "formset": formset, "action": "Create"})


@login_required
def chain_edit(request, pk):
    chain = get_object_or_404(ApprovalChain, pk=pk)
    if request.method == "POST":
        form = ApprovalChainForm(request.POST, instance=chain)
        formset = ApprovalStepFormSet(request.POST, instance=chain)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f"Approval chain '{chain.name}' updated.")
            return redirect("approvals:chain_list")
    else:
        form = ApprovalChainForm(instance=chain)
        formset = ApprovalStepFormSet(instance=chain)
    return render(request, "approvals/chain_form.html", {"form": form, "formset": formset, "action": "Edit"})


@login_required
def chain_delete(request, pk):
    chain = get_object_or_404(ApprovalChain, pk=pk)
    if request.method == "POST":
        name = chain.name
        chain.delete()
        messages.success(request, f"Approval chain '{name}' deleted.")
        return redirect("approvals:chain_list")
    return render(request, "contracts/confirm_delete.html", {"object": chain, "object_type": "Approval Chain"})
