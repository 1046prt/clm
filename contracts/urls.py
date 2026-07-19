from django.urls import path
from . import views

app_name = "contracts"

urlpatterns = [
    path("", views.contract_list, name="list"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("create/", views.contract_create, name="create"),
    path("upload/", views.contract_upload, name="upload"),
    path("<uuid:pk>/", views.contract_detail, name="detail"),
    path("<uuid:pk>/edit/", views.contract_edit, name="edit"),
    path("<uuid:pk>/delete/", views.contract_delete, name="delete"),
    path("<uuid:pk>/comment/", views.contract_add_comment, name="add_comment"),
    path("<uuid:pk>/analyze/", views.run_analysis, name="run_analysis"),
    path("parties/", views.party_list, name="party_list"),
    path("parties/create/", views.party_create, name="party_create"),
    path("parties/<uuid:pk>/edit/", views.party_edit, name="party_edit"),
    path("parties/<uuid:pk>/delete/", views.party_delete, name="party_delete"),
    path("clauses/", views.clause_list, name="clause_list"),
    path("clauses/<uuid:pk>/", views.clause_detail, name="clause_detail"),
    path("clauses/create/", views.clause_create, name="clause_create"),
    path("clauses/<uuid:pk>/edit/", views.clause_edit, name="clause_edit"),
    path("clauses/<uuid:pk>/delete/", views.clause_delete, name="clause_delete"),
    path("templates/", views.template_list, name="template_list"),
    path("templates/<uuid:pk>/", views.template_detail, name="template_detail"),
    path("templates/create/", views.template_create, name="template_create"),
    path("templates/<uuid:pk>/edit/", views.template_edit, name="template_edit"),
    path("templates/<uuid:pk>/delete/", views.template_delete, name="template_delete"),
    path("templates/<uuid:pk>/use/", views.template_use, name="template_use"),
]
