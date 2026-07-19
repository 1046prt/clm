import uuid
from django.db import models
from django.conf import settings


class AnalysisResult(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey(
        "contracts.Contract", on_delete=models.CASCADE, related_name="analysis_results"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    raw_response = models.JSONField(default=dict, blank=True)
    processing_time_seconds = models.FloatField(null=True, blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis of {self.contract.title} ({self.get_status_display()})"


class ExtractedMetadata(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.OneToOneField(AnalysisResult, on_delete=models.CASCADE, related_name="metadata")
    parties_involved = models.JSONField(default=list, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    renewal_terms = models.TextField(blank=True)
    payment_terms = models.TextField(blank=True)
    termination_clauses = models.TextField(blank=True)
    liability_cap = models.CharField(max_length=255, blank=True)
    governing_law = models.CharField(max_length=255, blank=True)
    jurisdiction = models.CharField(max_length=255, blank=True)
    non_compete_clause = models.BooleanField(default=False)
    confidentiality_clause = models.BooleanField(default=False)
    indemnification_clause = models.BooleanField(default=False)
    auto_renewal = models.BooleanField(default=False)
    force_majeure = models.BooleanField(default=False)
    extracted_text_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Extracted metadata"

    def __str__(self):
        return f"Metadata from {self.analysis.contract.title}"


class RiskFlag(models.Model):
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, related_name="risk_flags")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    category = models.CharField(max_length=100, help_text="Risk category (e.g., Auto-Renewal, Liability)")
    title = models.CharField(max_length=255)
    description = models.TextField()
    clause_reference = models.TextField(blank=True, help_text="The specific clause text that triggered this flag")
    recommendation = models.TextField(blank=True, help_text="Suggested action to mitigate this risk")
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-severity", "-created_at"]

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"

    @property
    def severity_badge_color(self):
        colors = {
            "low": "success",
            "medium": "warning",
            "high": "danger",
            "critical": "dark",
        }
        return colors.get(self.severity, "secondary")
