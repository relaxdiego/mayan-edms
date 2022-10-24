from pathlib import Path
import uuid

from django.conf import settings
from django.db import models
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.events.classes import EventManagerMethodAfter, EventManagerSave
from mayan.apps.events.decorators import method_event

from .classes import DefinedStorageLazy
from .events import (
    event_download_file_created, event_download_file_deleted,
    event_download_file_downloaded
)
from .literals import (
    STORAGE_NAME_DOWNLOAD_FILE, STORAGE_NAME_SHARED_UPLOADED_FILE
)
from .managers import DownloadFileManager, SharedUploadedFileManager
from .model_mixins import DatabaseFileModelMixin


def download_file_upload_to(instance, filename):
    return 'download-file-{}'.format(uuid.uuid4().hex)


def upload_to(instance, filename):
    return 'shared-file-{}'.format(uuid.uuid4().hex)


class DownloadFile(DatabaseFileModelMixin, ExtraDataModelMixin, models.Model):
    """
    Keep a database link to a stored file. Used for generated files meant
    to be downloaded at a later time.
    """

    file = models.FileField(
        storage=DefinedStorageLazy(
            name=STORAGE_NAME_DOWNLOAD_FILE
        ), upload_to=download_file_upload_to, verbose_name=_('File')
    )
    label = models.CharField(
        db_index=True, max_length=192, verbose_name=_('Label')
    )
    user = models.ForeignKey(
        editable=False, on_delete=models.CASCADE,
        related_name='download_files', to=settings.AUTH_USER_MODEL,
        verbose_name=_('User'),
    )

    objects = DownloadFileManager()

    class Meta:
        ordering = ('-datetime',)
        verbose_name = _('Download file')
        verbose_name_plural = _('Download files')

    def __str__(self):
        return self.filename or self.label

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_download_file_deleted
    )
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(viewname='storage:download_file_list')

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_download_file_downloaded,
        target='self'
    )
    def get_download_file_object(self):
        return self.open(mode='rb')

    def get_size_display(self):
        return filesizeformat(bytes_=self.file.size)

    get_size_display.short_description = _('Size')

    def get_user_display(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.user.username
    get_user_display.short_description = _('User')

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_download_file_created,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class SharedUploadedFile(DatabaseFileModelMixin, models.Model):
    """
    Keep a database link to a stored file. Used to share files between code
    that runs out of process.
    """

    file = models.FileField(
        storage=DefinedStorageLazy(
            name=STORAGE_NAME_SHARED_UPLOADED_FILE
        ), upload_to=upload_to, verbose_name=_('File')
    )
    filename = models.CharField(
        blank=True, max_length=255, verbose_name=_('Filename')
    )

    objects = SharedUploadedFileManager()

    class Meta:
        verbose_name = _('Shared uploaded file')
        verbose_name_plural = _('Shared uploaded files')

    def __str__(self):
        return self.filename

    def save(self, *args, **kwargs):
        self.filename = self.filename or Path(path=self.file.name).name
        super().save(*args, **kwargs)
        self.file.close()
