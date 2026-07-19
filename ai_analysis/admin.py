from django.contrib import admin
from .models import AnalysisResult, ExtractedMetadata, RiskFlag


class ExtractedMetadataInline(admin.StackedInline):
    model = ExtractedMetadata
    can_delete = False


class RiskFlagInline(admin.TabularInline):
    model = RiskFlag
    extra = 0


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ["contract", "status", "model_used", "tokens_used", "processing_time_seconds", "created_at"]
    list_filter = ["status", "model_used"]
    date_hierarchy = "created_at"
    inlines = [ExtractedMetadataInline, RiskFlagInline]


@admin.register(ExtractedMetadata)
class ExtractedMetadataAdmin(admin.ModelAdmin):
    list_display = ["analysis", "effective_date", "expiry_date", "auto_renewal", "governing_law"]


@admin.register(RiskFlag)
class RiskFlagAdmin(admin.ModelAdmin):
    list_display = ["analysis", "severity", "category", "title", "is_reviewed", "created_at"]
    list_filter = ["severity", "category", "is_reviewed"]
    search_fields = ["title", "description"]
