from django.urls import path
from . import views

app_name = "contracts"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("contracts/", views.contract_list, name="list"),
    path("contracts/create/", views.contract_create, name="create"),
    path("contracts/upload/", views.contract_upload, name="upload"),
    path("contracts/<uuid:pk>/", views.contract_detail, name="detail"),
    path("contracts/<uuid:pk>/edit/", views.contract_edit, name="edit"),
    path("contracts/<uuid:pk>/delete/", views.contract_delete, name="delete"),
    path("contracts/<uuid:pk>/comment/", views.contract_add_comment, name="add_comment"),
    path("contracts/<uuid:pk>/analyze/", views.run_analysis, name="analyze"),
]
