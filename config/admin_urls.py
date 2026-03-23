from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import AdminStatsView, AdminUserViewSet
from documents.views import AdminDocumentViewSet

app_name = "admin_api"

router = DefaultRouter()
router.register("users", AdminUserViewSet, basename="admin-user")
router.register("documents", AdminDocumentViewSet, basename="admin-document")

urlpatterns = [
    path("stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("", include(router.urls)),
]
