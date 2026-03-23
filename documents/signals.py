from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document, Section


@receiver(post_save, sender=Section)
def invalidate_on_section_change(sender, instance, **kwargs):
    document = instance.document
    if document.pdf_file:
        document.pdf_file.delete(save=False)
        Document.objects.filter(id=document.id).update(pdf_file="")


@receiver(post_save, sender=Document)
def invalidate_on_document_change(sender, instance, update_fields=None, **kwargs):
    if update_fields and not {"template", "theme", "template_id"}.intersection(update_fields or set()):
        return
    if instance.pdf_file:
        instance.pdf_file.delete(save=False)
        Document.objects.filter(id=instance.id).update(pdf_file="")
