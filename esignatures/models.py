import uuid
import hashlib
from django.db import models
from django.conf import settings


class SignatureRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("signed", "Signed"),
        ("completed", "Completed"),
        ("declined", "Declined"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey("contracts.Contract", on_delete=models.CASCADE, related_name="signature_requests")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    signer_name = models.CharField(max_length=255)
    signer_email = models.EmailField()
    signer_party = models.ForeignKey(
        "contracts.Party", on_delete=models.SET_NULL, null=True, blank=True
    )
    signing_order = models.PositiveIntegerField(default=1)
    message = models.TextField(blank=True, help_text="Personal message to the signer")
    expires_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["signing_order", "-created_at"]

    def __str__(self):
        return f"Signature request for {self.signer_name} on {self.contract.title}"


class Signature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(SignatureRequest, on_delete=models.CASCADE, related_name="signatures")
    signer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    signature_type = models.CharField(
        max_length=20,
        choices=[("drawn", "Drawn"), ("typed", "Typed"), ("uploaded", "Uploaded")],
        default="typed"
    )
    signature_data = models.TextField(
        help_text="Base64 encoded signature image or typed signature text"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    signature_hash = models.CharField(max_length=128, blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["signed_at"]

    def __str__(self):
        return f"Signature by {self.request.signer_name} at {self.signed_at}"

    def save(self, *args, **kwargs):
        if not self.signature_hash:
            hash_input = f"{self.request.id}{self.signature_data}{self.signed_at}"
            self.signature_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        super().save(*args, **kwargs)


class SigningAuditLog(models.Model):
    EVENT_CHOICES = [
        ("request_created", "Request Created"),
        ("request_sent", "Request Sent"),
        ("document_viewed", "Document Viewed"),
        ("signature_started", "Signature Started"),
        ("signature_completed", "Signature Completed"),
        ("request_completed", "All Signatures Collected"),
        ("request_declined", "Request Declined"),
        ("request_expired", "Request Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    signature_request = models.ForeignKey(
        SignatureRequest, on_delete=models.CASCADE, related_name="audit_logs"
    )
    event = models.CharField(max_length=30, choices=EVENT_CHOICES)
    actor_email = models.EmailField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        verbose_name_plural = "Signing audit logs"

    def __str__(self):
        return f"{self.get_event_display()} - {self.signature_request}"
