from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ..managers import DocumentFilePageManager, ValidDocumentFilePageManager

from .document_file_models import DocumentFile
from .document_file_page_model_mixins import DocumentFilePageBusinessLogicMixin
from .model_mixins import PagedModelMixin

__all__ = ('DocumentFilePage', 'DocumentFilePageSearchResult')


class DocumentFilePage(
    DocumentFilePageBusinessLogicMixin, PagedModelMixin, models.Model
):
    """
    Model that describes a document file page
    """
    _paged_model_parent_field = 'document_file'

    document_file = models.ForeignKey(
        on_delete=models.CASCADE, related_name='file_pages', to=DocumentFile,
        verbose_name=_('Document file')
    )
    page_number = models.PositiveIntegerField(
        db_index=True, default=1, editable=False,
        verbose_name=_('Page number')
    )

    objects = DocumentFilePageManager()
    valid = ValidDocumentFilePageManager()

    class Meta:
        ordering = ('page_number',)
        verbose_name = _('Document file page')
        verbose_name_plural = _('Document file pages')

    def __str__(self):
        return self.get_label()

    def delete(self, *args, **kwargs):
        self.cache_partition.delete()
        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            viewname='documents:document_file_page_view', kwargs={
                'document_file_page_id': self.pk
            }
        )

    def natural_key(self):
        return (
            self.page_number, self.document_file.natural_key()
        )
    natural_key.dependencies = ['documents.DocumentFile']


class DocumentFilePageSearchResult(DocumentFilePage):
    class Meta:
        ordering = ('document_file__document', 'page_number')
        proxy = True
        verbose_name = _('Document file page')
        verbose_name_plural = _('Document file pages')
