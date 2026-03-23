from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.http import JsonResponse
from django.views.generic import TemplateView


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    # Landing page
    path("", TemplateView.as_view(template_name="landing.html"), name="home"),

    # Admin
    path("admin-dashboard/", admin.site.urls),

    # Authentication (django-allauth)
    path("konto/", include("allauth.urls")),

    # Health check
    path("health/", health_check, name="health_check"),

    # --- API v1 ---
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/v1/admin/", include("config.admin_urls")),
    path("api/v1/users/", include("accounts.urls")),
    path("api/v1/documents/", include("documents.urls")),
    path("api/v1/payments/", include("payments.urls")),
    path("api/v1/legal/", include("legal.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
