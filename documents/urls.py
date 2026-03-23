from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "documents"

router = DefaultRouter()
router.register("", views.DocumentViewSet, basename="document")

urlpatterns = [
    path("templates/", views.TemplateListView.as_view(), name="template-list"),
    path("templates/<uuid:pk>/", views.TemplateDetailView.as_view(), name="template-detail"),
    path("themes/", views.ThemeListView.as_view(), name="theme-list"),
    path("", include(router.urls)),
]
