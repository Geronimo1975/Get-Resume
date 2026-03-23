from rest_framework import serializers
from .models import Document, Template, Section


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "section_type", "title", "content", "ordering", "is_visible"]


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for document listing."""
    class Meta:
        model = Document
        fields = [
            "id", "doc_type", "title", "template", "theme",
            "is_premium", "created_at", "updated_at",
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Full serializer with sections for editor."""
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            "id", "doc_type", "title", "content", "template", "theme",
            "is_premium", "pdf_file", "sections", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "pdf_file", "created_at", "updated_at"]


class AdminDocumentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    template_name = serializers.CharField(source="template.name", default=None, read_only=True)
    section_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id", "title", "doc_type", "user_email", "template_name",
            "is_premium", "created_at", "updated_at", "deleted_at", "section_count",
        ]


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            "id", "name", "slug", "category", "description",
            "thumbnail", "is_premium", "ordering",
        ]
