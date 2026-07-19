import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ApprovalChain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    contract_category = models.ForeignKey(
        "contracts.ContractCategory", on_delete=models.SET_NULL, null=True, blank=True,
        help_text="If set, this chain applies to contracts of this category"
    )
    min_value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text="Minimum contract value to trigger this chain"
    )
    max_value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True,
        help_text="Maximum contract value to trigger this chain"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def applies_to(self, contract):
        if not self.is_active:
            return False
        if self.contract_category and contract.category != self.contract_category:
            return False
        if self.min_value is not None and contract.total_value is not None:
            if contract.total_value < self.min_value:
                return False
        if self.max_value is not None and contract.total_value is not None:
            if contract.total_value > self.max_value:
                return False
        return True


class ApprovalStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chain = models.ForeignKey(ApprovalChain, on_delete=models.CASCADE, related_name="steps")
    step_number = models.PositiveIntegerField()
    name = models.CharField(max_length=255)
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="approval_steps"
   )
    role_required = models.CharField(
        max_length=100, blank=True,
        help_text="Role required to approve (e.g., 'legal', 'finance', 'manager')"
    )
    can_reject = models.BooleanField(default=True)
    can_comment = models.BooleanField(default=True)
    is_optional = models.BooleanField(default=False)

    class Meta:
        ordering = ["step_number"]
        unique_together = ["chain", "step_number"]

    def __str__(self):
        return f"{self.chain.name} - Step {self.step_number}: {self.name}"


class ApprovalRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey("contracts.Contract", on_delete=models.CASCADE, related_name="approval_requests")
    chain = models.ForeignKey(ApprovalChain, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    current_step = models.ForeignKey(
        ApprovalStep, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="current_approvals"
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="initiated_approvals"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Approval for {self.contract.title} ({self.get_status_display()})"

    @property
    def progress_percentage(self):
        if not self.chain:
            return 0
        total_steps = self.chain.steps.count()
        if total_steps == 0:
            return 0
        completed = self.action_logs.filter(action="approve").count()
        return int((completed / total_steps) * 100)


class ApprovalAction(models.Model):
    ACTION_CHOICES = [
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("comment", "Comment"),
        ("request_changes", "Request Changes"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    approval_request = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE, related_name="action_logs")
    step = models.ForeignKey(ApprovalStep, on_delete=models.SET_NULL, null=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.actor} - {self.get_action_display()} on {self.approval_request.contract.title}"
