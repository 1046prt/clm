from django.urls import path
from . import views

app_name = "approvals"

urlpatterns = [
    path("", views.approval_list, name="list"),
    path("<uuid:pk>/", views.approval_detail, name="detail"),
    path("<uuid:pk>/process/", views.process_approval_view, name="process"),
    path("initiate/<uuid:pk>/", views.initiate_approval_view, name="initiate"),
    path("chains/", views.chain_list, name="chain_list"),
    path("chains/<uuid:pk>/", views.chain_detail, name="chain_detail"),
    path("chains/create/", views.chain_create, name="chain_create"),
    path("chains/<uuid:pk>/edit/", views.chain_edit, name="chain_edit"),
    path("chains/<uuid:pk>/delete/", views.chain_delete, name="chain_delete"),
]
