from django import forms
from .models import Obligation, ObligationCategory

_OBLIGATION_FIELDS = [
    "contract", "category", "title", "description",
    "responsible_party", "assigned_to",
    "frequency", "status", "due_date", "start_date", "end_date",
    "penalty_for_breach", "reminder_days_before",
]


class ObligationForm(forms.ModelForm):
    class Meta:
        model = Obligation
        fields = _OBLIGATION_FIELDS
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "penalty_for_breach": forms.Textarea(attrs={"rows": 3}),
        }


class ObligationCreateForm(ObligationForm):
    class Meta:
        model = Obligation
        fields = [f for f in _OBLIGATION_FIELDS if f not in ("status",)]
        widgets = ObligationForm.Meta.widgets
