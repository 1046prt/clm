from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("contracts.urls")),
    path("approvals/", include("approvals.urls")),
    path("ai/", include("ai_analysis.urls")),
    path("obligations/", include("obligations.urls")),
    path("esign/", include("esignatures.urls")),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
