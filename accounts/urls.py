from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer, UserProfileSerializer

app_name = "accounts"


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    """Current user profile."""
    if request.method == "GET":
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    serializer = UserProfileSerializer(request.user.profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def gdpr_export(request):
    """Request GDPR data export (Art. 20 DSGVO)."""
    # TODO: Create GDPRRequest + dispatch Celery task
    return Response({"status": "export_requested"}, status=202)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def gdpr_delete(request):
    """Request account deletion (Art. 17 DSGVO)."""
    # TODO: Create GDPRRequest + dispatch Celery task
    return Response({"status": "deletion_requested"}, status=202)


urlpatterns = [
    path("me/", me, name="me"),
    path("me/gdpr/export/", gdpr_export, name="gdpr-export"),
    path("me/gdpr/delete/", gdpr_delete, name="gdpr-delete"),
]
