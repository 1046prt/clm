from django.contrib import admin
from .models import ObligationCategory, Obligation, RenewalAlert


@admin.register(ObligationCategory)
class ObligationCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(Obligation)
class ObligationAdmin(admin.ModelAdmin):
    list_display = [
        "title", "contract", "frequency", "status",
        "due_date", "assigned_to", "responsible_party"
    ]
    list_filter = ["status", "frequency"]
    search_fields = ["title", "description"]
    date_hierarchy = "due_date"


@admin.register(RenewalAlert)
class RenewalAlertAdmin(admin.ModelAdmin):
    list_display = ["contract", "alert_type", "days_until_event", "is_read", "is_dismissed", "created_at"]
    list_filter = ["alert_type", "is_read", "is_dismissed"]
    filter_horizontal = ["notified_users"]
