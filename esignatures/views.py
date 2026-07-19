from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
import hashlib

from .models import SignatureRequest, Signature, SigningAuditLog
from contracts.models import Contract


@login_required
def create_signature_request(request, contract_pk):
    contract = get_object_or_404(Contract, pk=contract_pk)

    if request.method == "POST":
        signer_name = request.POST.get("signer_name", "")
        signer_email = request.POST.get("signer_email", "")
        message_text = request.POST.get("message", "")

        if not signer_name or not signer_email:
            messages.error(request, "Signer name and email are required.")
            return redirect("esign:create_request", contract_pk=contract_pk)

        sig_request = SignatureRequest.objects.create(
            contract=contract,
            signer_name=signer_name,
            signer_email=signer_email,
            message=message_text,
            status="pending",
        )

        SigningAuditLog.objects.create(
            signature_request=sig_request,
            event="request_created",
            actor_email=request.user.email,
        )

        messages.success(request, f"Signature request created for {signer_name}.")
        return redirect("contracts:detail", pk=contract_pk)

    return render(request, "esignatures/create_request.html", {"contract": contract})


@login_required
def sign_document(request, pk):
    sig_request = get_object_or_404(
        SignatureRequest.objects.select_related("contract"),
        pk=pk,
    )

    if request.method == "POST":
        signature_data = request.POST.get("signature_data", "")
        signature_type = request.POST.get("signature_type", "typed")

        if not signature_data:
            messages.error(request, "Signature is required.")
            return redirect("esign:sign", pk=pk)

        signature = Signature.objects.create(
            request=sig_request,
            signature_type=signature_type,
            signature_data=signature_data,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        sig_request.status = "signed"
        sig_request.save()

        SigningAuditLog.objects.create(
            signature_request=sig_request,
            event="signature_completed",
            actor_email=sig_request.signer_email,
            ip_address=_get_client_ip(request),
            details={"signature_hash": signature.signature_hash},
        )

        all_signed = not SignatureRequest.objects.filter(
            contract=sig_request.contract,
            status__in=["pending", "sent"],
        ).exists()

        if all_signed:
            sig_request.contract.status = "active"
            sig_request.contract.save()
            sig_request.status = "completed"
            sig_request.save()
            SigningAuditLog.objects.create(
                signature_request=sig_request,
                event="request_completed",
            )
            messages.success(request, "All signatures collected. Contract is now active!")
        else:
            messages.success(request, "Your signature has been recorded.")

        return redirect("contracts:detail", pk=sig_request.contract.pk)

    SigningAuditLog.objects.create(
        signature_request=sig_request,
        event="document_viewed",
        actor_email=sig_request.signer_email,
        ip_address=_get_client_ip(request),
    )

    return render(request, "esignatures/sign.html", {"sig_request": sig_request})


@login_required
def signature_audit_log(request, contract_pk):
    contract = get_object_or_404(Contract, pk=contract_pk)
    logs = SigningAuditLog.objects.filter(
        signature_request__contract=contract
    ).select_related("signature_request").order_by("-timestamp")

    return render(request, "esignatures/audit_log.html", {
        "contract": contract,
        "logs": logs,
    })


def _get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
