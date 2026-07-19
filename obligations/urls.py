from django.urls import path
from . import views

app_name = "obligations"

urlpatterns = [
    path("", views.obligation_dashboard, name="dashboard"),
    path("list/", views.obligation_list, name="list"),
    path("alert/<uuid:pk>/dismiss/", views.dismiss_alert, name="dismiss_alert"),
]
