from django.contrib import admin
from .models import (
    Party, ContractCategory, ClauseCategory, Clause,
    ContractTemplate, Contract, ContractVersion, ContractComment
)


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ["name", "party_type", "email", "created_at"]
    search_fields = ["name", "email"]
    list_filter = ["party_type"]


@admin.register(ContractCategory)
class ContractCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(ClauseCategory)
class ClauseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(Clause)
class ClauseAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "risk_level", "is_pre_approved", "version"]
    list_filter = ["risk_level", "is_pre_approved", "category"]
    search_fields = ["title", "content"]


@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_active", "version", "created_at"]
    list_filter = ["is_active", "category"]
    search_fields = ["name", "description"]


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["title", "contract_number", "status", "priority", "effective_date", "expiry_date", "total_value"]
    list_filter = ["status", "priority", "category", "auto_renew"]
    search_fields = ["title", "contract_number", "description"]
    filter_horizontal = ["parties"]
    date_hierarchy = "created_at"


@admin.register(ContractVersion)
class ContractVersionAdmin(admin.ModelAdmin):
    list_display = ["contract", "version_number", "created_by", "created_at"]
    list_filter = ["created_at"]


@admin.register(ContractComment)
class ContractCommentAdmin(admin.ModelAdmin):
    list_display = ["contract", "author", "is_internal", "created_at"]
    list_filter = ["is_internal"]
