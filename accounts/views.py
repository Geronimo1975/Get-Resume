from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import timedelta

from config.permissions import IsStaffUser
from .models import User, UserProfile
from .serializers import AdminUserListSerializer, AdminUserDetailSerializer
from documents.models import Document


class AdminStatsView(APIView):
    """GET /api/v1/admin/stats/ — Dashboard overview stats."""
    permission_classes = [IsStaffUser]

    def get(self, request):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        # User stats
        total_users = User.objects.count()
        active_30d = User.objects.filter(last_login__gte=thirty_days_ago).count()
        new_today = User.objects.filter(date_joined__gte=today_start).count()
        premium_count = UserProfile.objects.exclude(subscription_plan="free").count()
        free_count = total_users - premium_count

        # Document stats (excluding soft-deleted)
        total_docs = Document.objects.count()
        docs_today = Document.objects.filter(created_at__gte=today_start).count()
        docs_7d = Document.objects.filter(created_at__gte=seven_days_ago).count()
        by_type = {
            "lebenslauf": Document.objects.filter(doc_type="lebenslauf").count(),
            "anschreiben": Document.objects.filter(doc_type="anschreiben").count(),
            "deckblatt": Document.objects.filter(doc_type="deckblatt").count(),
        }

        # System info
        db_size = "--"
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_database_size(current_database())")
                size_bytes = cursor.fetchone()[0]
                db_size = f"{size_bytes / (1024 * 1024):.1f} MB"
        except Exception:
            pass

        # Recent signups (last 10)
        recent_signups = list(
            User.objects.order_by("-date_joined")[:10].values(
                "id", "email", "first_name", "last_name", "date_joined"
            )
        )

        # Recent documents (last 10, all users)
        recent_docs_qs = Document.objects.select_related("user").order_by("-created_at")[:10]
        recent_documents = [
            {
                "id": str(doc.id),
                "title": doc.title,
                "doc_type": doc.doc_type,
                "user_email": doc.user.email,
                "created_at": doc.created_at.isoformat(),
            }
            for doc in recent_docs_qs
        ]

        # Subscription breakdown
        plan_counts = dict(
            UserProfile.objects.values_list("subscription_plan").annotate(c=Count("id")).values_list("subscription_plan", "c")
        )

        return Response({
            "users": {
                "total": total_users,
                "active_30d": active_30d,
                "new_today": new_today,
                "premium": premium_count,
                "free": free_count,
            },
            "documents": {
                "total": total_docs,
                "created_today": docs_today,
                "created_7d": docs_7d,
                "by_type": by_type,
            },
            "system": {
                "uptime": "--",
                "version": "1.0.0",
                "db_size": db_size,
                "redis_memory": "--",
            },
            "recent_signups": recent_signups,
            "recent_documents": recent_documents,
            "subscriptions": {
                "free": plan_counts.get("free", 0),
                "premium_monthly": plan_counts.get("premium_monthly", 0),
                "premium_yearly": plan_counts.get("premium_yearly", 0),
                "business": plan_counts.get("business", 0),
            },
        })


class AdminUserViewSet(viewsets.ModelViewSet):
    """Admin user management — list, detail, update, deactivate."""
    permission_classes = [IsStaffUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["date_joined", "last_login", "email"]
    ordering = ["-date_joined"]

    def get_queryset(self):
        qs = User.objects.select_related("profile").annotate(
            document_count=Count("documents")
        )
        # Filters
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        is_staff = self.request.query_params.get("is_staff")
        if is_staff is not None:
            qs = qs.filter(is_staff=is_staff.lower() == "true")
        plan = self.request.query_params.get("subscription_plan")
        if plan:
            qs = qs.filter(profile__subscription_plan=plan)
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AdminUserDetailSerializer
        return AdminUserListSerializer

    def perform_destroy(self, instance):
        """Deactivate user instead of hard delete."""
        instance.is_active = False
        instance.save(update_fields=["is_active"])

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        return Response({"is_active": user.is_active})

    @action(detail=True, methods=["post"])
    def toggle_staff(self, request, pk=None):
        user = self.get_object()
        user.is_staff = not user.is_staff
        user.save(update_fields=["is_staff"])
        return Response({"is_staff": user.is_staff})
