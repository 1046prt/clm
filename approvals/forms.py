from django import forms
from .models import ApprovalChain, ApprovalStep, ApprovalRequest
from contracts.models import ContractCategory


class ApprovalChainForm(forms.ModelForm):
    class Meta:
        model = ApprovalChain
        fields = ["name", "description", "contract_category", "min_value", "max_value", "is_active"]


class ApprovalStepForm(forms.ModelForm):
    class Meta:
        model = ApprovalStep
        fields = ["step_number", "name", "approver", "role_required", "can_reject", "can_comment", "is_optional"]


ApprovalStepFormSet = forms.inlineformset_factory(
    ApprovalChain, ApprovalStep, form=ApprovalStepForm,
    extra=1, can_delete=True, min_num=1,
)


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
