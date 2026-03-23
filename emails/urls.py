from django.urls import path

app_name = "emails"

# Email credential management is under accounts/urls.py
# This app provides Celery tasks only (no direct URL endpoints)
urlpatterns = []
