from django.urls import path
from . import views

app_name = "esign"

urlpatterns = [
    path("", views.signature_request_list, name="list"),
    path("request/<uuid:contract_pk>/", views.create_signature_request, name="create_request"),
    path("sign/<uuid:pk>/", views.sign_document, name="sign"),
    path("audit/<uuid:contract_pk>/", views.signature_audit_log, name="audit_log"),
]
