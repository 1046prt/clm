from django import forms
from .models import (
    Contract, Party, ContractCategory, ContractTemplate, Clause,
    ClauseCategory, ContractComment, ContractVersion
)


class ContractForm(forms.ModelForm):
    parties = forms.ModelMultipleChoiceField(
        queryset=Party.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Contract
        fields = [
            "title", "description", "category", "template", "priority",
            "parties", "effective_date", "expiry_date", "renewal_date",
            "auto_renew", "renewal_notice_days", "total_value", "currency",
            "content", "is_confidential",
        ]
        widgets = {
            "effective_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
            "renewal_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 10}),
        }


class ContractUploadForm(forms.Form):
    file = forms.FileField(
        help_text="Upload a PDF or DOCX contract file",
        widget=forms.FileInput(attrs={"accept": ".pdf,.docx,.doc"}),
    )
    title = forms.CharField(max_length=255)
    category = forms.ModelChoiceField(
        queryset=ContractCategory.objects.all(),
        required=False,
    )
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)


class ContractSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Search contracts..."}),
    )
    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + Contract.STATUS_CHOICES,
        required=False,
    )
    category = forms.ModelChoiceField(
        queryset=ContractCategory.objects.all(),
        required=False,
        empty_label="All Categories",
    )
    priority = forms.ChoiceField(
        choices=[("", "All Priorities")] + Contract.PRIORITY_CHOICES,
        required=False,
    )


class ContractCommentForm(forms.ModelForm):
    class Meta:
        model = ContractComment
        fields = ["content", "is_internal"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a comment..."}),
        }


# ── Party CRUD ───────────────────────────────

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ["name", "party_type", "email", "phone", "address", "tax_id", "contact_person"]


# ── Clause CRUD ──────────────────────────────

class ClauseForm(forms.ModelForm):
    class Meta:
        model = Clause
        fields = ["title", "category", "content", "risk_level", "is_pre_approved", "version", "tags"]
        widgets = {"content": forms.Textarea(attrs={"rows": 6})}


# ── ContractTemplate CRUD ────────────────────

class ContractTemplateForm(forms.ModelForm):
    clauses = forms.ModelMultipleChoiceField(
        queryset=Clause.objects.filter(is_pre_approved=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = ContractTemplate
        fields = ["name", "category", "description", "content", "is_active", "version", "clauses"]
        widgets = {"content": forms.Textarea(attrs={"rows": 10})}
