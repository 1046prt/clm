import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class ObligationCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Obligation categories"

    def __str__(self):
        return self.name


class Obligation(models.Model):
    FREQUENCY_CHOICES = [
        ("once", "One-time"),
        ("weekly", "Weekly"),
        ("biweekly", "Bi-weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("semi_annual", "Semi-Annual"),
        ("annual", "Annual"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("overdue", "Overdue"),
        ("waived", "Waived"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey("contracts.Contract", on_delete=models.CASCADE, related_name="obligations")
    category = models.ForeignKey(ObligationCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    responsible_party = models.ForeignKey(
        "contracts.Party", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="obligations"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_obligations"
    )

    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default="once")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    due_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)

    penalty_for_breach = models.TextField(blank=True, help_text="Description of penalties for non-compliance")
    reminder_days_before = models.PositiveIntegerField(default=7)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_frequency_display()})"

    @property
    def is_overdue(self):
        if self.status in ("completed", "waived"):
            return False
        if self.due_date and self.due_date < timezone.now().date():
            return True
        return False

    @property
    def days_until_due(self):
        if not self.due_date:
            return None
        return (self.due_date - timezone.now().date()).days


class RenewalAlert(models.Model):
    ALERT_TYPE_CHOICES = [
        ("expiry_warning", "Expiry Warning"),
        ("renewal_due", "Renewal Due"),
        ("auto_renew_warning", "Auto-Renew Warning"),
        ("obligation_due", "Obligation Due"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contract = models.ForeignKey("contracts.Contract", on_delete=models.CASCADE, related_name="renewal_alerts")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    message = models.TextField()
    days_until_event = models.IntegerField(help_text="Days until the event (negative = overdue)")
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    notified_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_alert_type_display()} for {self.contract.title}"
