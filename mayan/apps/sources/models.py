from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import (
    BackendModelMixin, ExtraDataModelMixin
)
from mayan.apps.events.classes import EventManagerSave
from mayan.apps.events.decorators import method_event

from .classes import SourceBackendNull
from .events import event_source_created, event_source_edited
from .managers import SourceManager
from .model_mixins import SourceBusinessLogicMixin


class Source(
    BackendModelMixin, ExtraDataModelMixin, SourceBusinessLogicMixin,
    models.Model
):
    _backend_model_null_backend = SourceBackendNull

    label = models.CharField(
        db_index=True, help_text=_('A short text to describe this source.'),
        max_length=128, unique=True, verbose_name=_('Label')
    )
    enabled = models.BooleanField(
        default=True, verbose_name=_('Enabled')
    )

    objects = SourceManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Source')
        verbose_name_plural = _('Sources')

    def __str__(self):
        return '%s' % self.label

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            self.get_backend_instance().delete()
            super().delete(*args, **kwargs)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_source_created,
            'target': 'self',
        },
        edited={
            'event': event_source_edited,
            'target': 'self',
        }
    )
    def save(self, *args, **kwargs):
        is_new = not self.pk

        with transaction.atomic():
            super().save(*args, **kwargs)

            self.get_backend_instance().clean()

            if is_new:
                self.get_backend_instance().create()
            else:
                self.get_backend_instance().save()
