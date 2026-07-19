import uuid
import os
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


def contract_upload_path(instance, filename):
    return f"contracts/{instance.id}/{filename}"


class Party(models.Model):
    PARTY_TYPE_CHOICES = [
        ("individual", "Individual"),
        ("company", "Company"),
        ("government", "Government Entity"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    party_type = models.CharField(max_length=20, choices=PARTY_TYPE_CHOICES, default="company")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True, verbose_name="Tax ID / EIN")
    contact_person = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ContractCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color for UI badges")

    class Meta:
        verbose_name_plural = "Contract categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClauseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Clause(models.Model):
    RISK_LEVEL_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(ClauseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField(help_text="The clause text/content")
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, default="low")
    is_pre_approved = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default="1.0")
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "title"]

    def __str__(self):
        return self.title


class ContractTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ContractCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    content = models.TextField(help_text="Template body with {{variable}} placeholders")
    clauses = models.ManyToManyField(Clause, blank=True, related_name="templates")
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20, default="1.0")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contract(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending_approval", "Pending Approval"),
        ("in_review", "In Review"),
        ("approved", "Approved"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("terminated", "Terminated"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    contract_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ContractCategory, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey(ContractTemplate, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")

    parties = models.ManyToManyField(Party, related_name="contracts")
    internal_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="owned_contracts"
    )

    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    renewal_date = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    renewal_notice_days = models.PositiveIntegerField(
        default=30, help_text="Days before expiry to send renewal notice"
    )

    total_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")

    uploaded_file = models.FileField(upload_to=contract_upload_path, blank=True, null=True)
    content = models.TextField(blank=True, help_text="Contract body text")

    version = models.CharField(max_length=20, default="1.0")
    is_confidential = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="created_contracts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("contracts:detail", kwargs={"pk": self.pk})

    @property
    def is_expiring_soon(self):
        if not self.expiry_date:
            return False
        days_until = (self.expiry_date - timezone.now().date()).days
        return 0 < days_until <= self.renewal_notice_days

    @property
    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.now().date()).days

    @property
    def status_badge_color(self):
        colors = {
            "draft": "secondary",
            "pending_approval": "warning",
            "in_review": "info",
            "approved": "primary",
            "active": "success",
            "expired": "danger",
            "terminated": "dark",
            "cancelled": "muted",
        }
        return colors.get(self.status, "secondary")


class ContractVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="versions")
    version_number = models.CharField(max_length=20)
    content = models.TextField()
    changes_summary = models.TextField(blank=True)
    file_snapshot = models.FileField(upload_to=contract_upload_path, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version_number"]
        unique_together = ["contract", "version_number"]

    def __str__(self):
        return f"{self.contract.title} v{self.version_number}"


class ContractComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    is_internal = models.BooleanField(default=True, help_text="Internal notes not visible to external parties")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.contract.title} by {self.author}"
