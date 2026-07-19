from django.contrib import admin
from .models import (
    ApprovalChain, ApprovalStep, ApprovalRequest, ApprovalAction
)


class ApprovalStepInline(admin.TabularInline):
    model = ApprovalStep
    extra = 1
    ordering = ["step_number"]


@admin.register(ApprovalChain)
class ApprovalChainAdmin(admin.ModelAdmin):
    list_display = ["name", "contract_category", "min_value", "max_value", "is_active"]
    list_filter = ["is_active"]
    inlines = [ApprovalStepInline]


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    list_display = ["chain", "step_number", "name", "approver", "is_optional"]
    list_filter = ["chain"]


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ["contract", "status", "requested_by", "created_at", "completed_at"]
    list_filter = ["status"]
    date_hierarchy = "created_at"


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    list_display = ["approval_request", "actor", "action", "created_at"]
    list_filter = ["action"]
