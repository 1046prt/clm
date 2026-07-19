import logging
from django.utils import timezone
from django.contrib.auth.models import User

from approvals.models import ApprovalChain, ApprovalRequest, ApprovalStep, ApprovalAction
from contracts.models import Contract

logger = logging.getLogger(__name__)


def initiate_approval(contract, user, notes=""):
    chain = _find_matching_chain(contract)
    if not chain:
        logger.warning(f"No approval chain found for contract {contract.id}")
        return None

    approval_request = ApprovalRequest.objects.create(
        contract=contract,
        chain=chain,
        requested_by=user,
        notes=notes,
        status="in_progress",
    )

    first_step = chain.steps.order_by("step_number").first()
    if first_step:
        approval_request.current_step = first_step
        approval_request.save()

    contract.status = "pending_approval"
    contract.save()

    _create_action_log(approval_request, first_step, user, "comment", "Approval process initiated")
    _notify_approver(first_step, contract)

    return approval_request


def process_approval(approval_request, step, user, action, comment=""):
    if action not in ("approve", "reject", "request_changes"):
        raise ValueError(f"Invalid action: {action}")

    log = _create_action_log(approval_request, step, user, action, comment)

    if action == "reject":
        approval_request.status = "rejected"
        approval_request.completed_at = timezone.now()
        approval_request.save()
        approval_request.contract.status = "draft"
        approval_request.contract.save()
        _notify_requester(approval_request, "rejected")
        return approval_request

    if action == "request_changes":
        approval_request.status = "pending"
        approval_request.current_step = step
        approval_request.save()
        approval_request.contract.status = "in_review"
        approval_request.contract.save()
        _notify_requester(approval_request, "changes_requested")
        return approval_request

    next_step = _get_next_step(approval_request, step)
    if next_step:
        approval_request.current_step = next_step
        approval_request.save()
        _notify_approver(next_step, approval_request.contract)
    else:
        approval_request.status = "approved"
        approval_request.current_step = None
        approval_request.completed_at = timezone.now()
        approval_request.save()
        approval_request.contract.status = "approved"
        approval_request.contract.save()
        _notify_requester(approval_request, "approved")

    return approval_request


def _find_matching_chain(contract):
    chains = ApprovalChain.objects.filter(is_active=True)
    for chain in chains:
        if chain.applies_to(contract):
            return chain
    return None


def _get_next_step(approval_request, current_step):
    if not approval_request.chain:
        return None
    steps = approval_request.chain.steps.order_by("step_number")
    found = False
    for step in steps:
        if found:
            return step
        if step.id == current_step.id:
            found = True
    return None


def _create_action_log(approval_request, step, user, action, comment=""):
    return ApprovalAction.objects.create(
        approval_request=approval_request,
        step=step,
        actor=user,
        action=action,
        comment=comment,
    )


def _notify_approver(step, contract):
    logger.info(f"Notifying {step.approver.username} about {contract.title}")
    # In production: send email / push notification / Celery task
    # For now, just log it


def _notify_requester(approval_request, event_type):
    user = approval_request.requested_by
    if user:
        logger.info(f"Notifying {user.username} that {approval_request.contract.title} was {event_type}")
        # In production: send email / push notification
