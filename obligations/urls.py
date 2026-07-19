from django.urls import path
from . import views

app_name = "obligations"

urlpatterns = [
    path("", views.obligation_dashboard, name="dashboard"),
    path("list/", views.obligation_list, name="list"),
    path("create/", views.obligation_create, name="create"),
    path("<uuid:pk>/edit/", views.obligation_edit, name="edit"),
    path("<uuid:pk>/complete/", views.obligation_complete, name="complete"),
    path("<uuid:pk>/delete/", views.obligation_delete, name="delete"),
    path("dismiss-alert/<uuid:pk>/", views.dismiss_alert, name="dismiss_alert"),
]
