from django.urls import path
from . import views

app_name = "ai_analysis"

urlpatterns = [
    path("<uuid:pk>/", views.analysis_detail, name="detail"),
    path("risk/<uuid:pk>/review/", views.mark_risk_reviewed, name="mark_risk_reviewed"),
]
