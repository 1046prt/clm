from django.contrib import admin
from .models import SignatureRequest, Signature, SigningAuditLog


@admin.register(SignatureRequest)
class SignatureRequestAdmin(admin.ModelAdmin):
    list_display = ["contract", "signer_name", "signer_email", "status", "signing_order", "created_at"]
    list_filter = ["status"]
    search_fields = ["signer_name", "signer_email"]


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ["request", "signature_type", "signed_at", "signature_hash"]
    list_filter = ["signature_type"]


@admin.register(SigningAuditLog)
class SigningAuditLogAdmin(admin.ModelAdmin):
    list_display = ["signature_request", "event", "actor_email", "timestamp"]
    list_filter = ["event"]
    date_hierarchy = "timestamp"
