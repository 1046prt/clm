from django import forms
from .models import ApprovalChain, ApprovalRequest


class ApprovalActionForm(forms.Form):
    ACTION_CHOICES = [
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("request_changes", "Request Changes"),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect)
    comment = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Add a comment (optional)"}),
        required=False,
    )


class InitiateApprovalForm(forms.Form):
    chain = forms.ModelChoiceField(
        queryset=ApprovalChain.objects.filter(is_active=True),
        required=False,
        empty_label="Auto-detect chain",
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Notes for approvers..."}),
        required=False,
    )
