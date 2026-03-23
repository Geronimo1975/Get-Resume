from django.db.models import Count
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from config.permissions import IsStaffUser
from .models import Document, Template
from .serializers import (
    DocumentListSerializer,
    DocumentDetailSerializer,
    AdminDocumentSerializer,
    TemplateSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    """CRUD for user documents (Lebenslauf, Anschreiben, Deckblatt)."""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["doc_type"]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).select_related("template")

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentListSerializer
        return DocumentDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete()

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """Clone a document."""
        original = self.get_object()
        clone = Document.objects.create(
            user=request.user,
            doc_type=original.doc_type,
            title=f"{original.title} (Kopie)",
            content=original.content,
            template=original.template,
            theme=original.theme,
        )
        return Response(DocumentDetailSerializer(clone).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def preview(self, request, pk=None):
        """Render HTML preview for the editor iframe."""
        document = self.get_object()
        # TODO: Render HTML from content + template + theme
        return Response({"html": "<p>Preview coming soon</p>"})

    @action(detail=True, methods=["get"], url_path="ats-score")
    def ats_score(self, request, pk=None):
        """Calculate ATS compatibility score."""
        document = self.get_object()
        # TODO: ATS scoring logic
        return Response({"score": 0, "suggestions": []})

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        """Generate and return PDF."""
        document = self.get_object()
        # TODO: WeasyPrint PDF generation
        return Response({"status": "pdf_generation_not_implemented"}, status=501)


class TemplateListView(generics.ListAPIView):
    """Public template catalog."""
    serializer_class = TemplateSerializer
    permission_classes = [AllowAny]
    queryset = Template.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "is_premium"]


class TemplateDetailView(generics.RetrieveAPIView):
    """Template detail."""
    serializer_class = TemplateSerializer
    permission_classes = [AllowAny]
    queryset = Template.objects.filter(is_active=True)


class ThemeListView(generics.ListAPIView):
    """List available color themes."""
    permission_classes = [AllowAny]

    def list(self, request):
        # TODO: Move themes to database model
        themes = [
            {"id": "default", "name": "Standard Blau", "primary": "#2563eb", "is_premium": False},
            {"id": "emerald", "name": "Smaragd", "primary": "#059669", "is_premium": False},
            {"id": "slate", "name": "Schiefer", "primary": "#475569", "is_premium": False},
        ]
        return Response(themes)


class AdminDocumentViewSet(viewsets.ModelViewSet):
    """Admin document management — includes soft-deleted documents."""
    permission_classes = [IsStaffUser]
    serializer_class = AdminDocumentSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "user__email"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Document.all_objects.select_related("user", "template").annotate(
            section_count=Count("sections")
        )
        doc_type = self.request.query_params.get("doc_type")
        if doc_type:
            qs = qs.filter(doc_type=doc_type)
        is_deleted = self.request.query_params.get("is_deleted")
        if is_deleted is not None:
            if is_deleted.lower() == "true":
                qs = qs.filter(deleted_at__isnull=False)
            else:
                qs = qs.filter(deleted_at__isnull=True)
        return qs

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        doc = self.get_object()
        doc.restore()
        return Response({"status": "restored"})

    def perform_destroy(self, instance):
        """Hard delete for admin."""
        instance.delete()
