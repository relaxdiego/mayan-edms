from furl import furl
from zipfile import ZipFile

from django.apps import apps
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.locales.utils import to_language

from .literals import (
    DOCUMENT_FILE_DOWNLOAD_MESSAGE_BODY,
    DOCUMENT_FILE_DOWNLOAD_MESSAGE_SUBJECT
)


class DocumentFileCompressor:
    def __init__(self, queryset):
        self.queryset = queryset

    def compress(self, file_object, _event_action_object=None, _event_actor=None):
        with ZipFile(file=file_object, mode='w') as archive:
            for document_file in self.queryset.all():
                document_file._event_action_object = _event_action_object
                document_file._event_actor = _event_actor
                with document_file.get_download_file_object() as file_object:
                    archive.write(
                        arcname=str(document_file),
                        filename=file_object.name
                    )

    def compress_to_download_file(
        self, organization_installation_url='', filename=None, user=None
    ):
        DownloadFile = apps.get_model(
            app_label='storage', model_name='DownloadFile'
        )
        Message = apps.get_model(
            app_label='messaging', model_name='Message'
        )

        if self.queryset.count():
            filename = filename or _('Document_file_bundle.zip')

            download_file = DownloadFile(
                filename=filename, label=_('Compressed document files'),
                user=user
            )
            download_file._event_actor = user
            download_file.save()

            with download_file.open(mode='wb+') as file_object:
                self.compress(
                    file_object=file_object,
                    _event_action_object=download_file,
                    _event_actor=user
                )

            if user:
                download_list_url = furl(organization_installation_url).join(
                    reverse(
                        viewname='storage:download_file_list'
                    )
                ).tostr()

                download_url = furl(organization_installation_url).join(
                    reverse(
                        viewname='storage:download_file_download',
                        kwargs={'download_file_id': download_file.pk}
                    )
                ).tostr()

                Message.objects.create(
                    sender_object=download_file,
                    user=user,
                    subject=to_language(
                        language=user.locale_profile.language,
                        promise=DOCUMENT_FILE_DOWNLOAD_MESSAGE_SUBJECT
                    ),
                    body=to_language(
                        language=user.locale_profile.language,
                        promise=DOCUMENT_FILE_DOWNLOAD_MESSAGE_BODY
                    ) % {
                        'download_list_url': download_list_url,
                        'download_url': download_url
                    }
                )
