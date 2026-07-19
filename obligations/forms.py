from django import forms
from .models import Obligation, ObligationCategory


class ObligationForm(forms.ModelForm):
    class Meta:
        model = Obligation
        fields = [
            "contract", "category", "title", "description",
            "responsible_party", "assigned_to",
            "frequency", "status", "due_date", "start_date", "end_date",
            "penalty_for_breach", "reminder_days_before",
        ]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "penalty_for_breach": forms.Textarea(attrs={"rows": 3}),
        }
