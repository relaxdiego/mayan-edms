import logging

from django.apps import apps

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.serialization import yaml_load

from ..classes import BaseDocumentFilenameGenerator
from ..permissions import permission_document_view
from ..settings import setting_language

logger = logging.getLogger(name=__name__)


class DocumentTypeBusinessLogicMixin:
    @property
    def trashed_documents(self):
        TrashedDocument = apps.get_model(
            app_label='documents', model_name='TrashedDocument'
        )

        return TrashedDocument.objects.filter(document_type=self)

    def get_document_count(self, user):
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view, queryset=self.documents,
            user=user
        )

        return queryset.count()

    def get_upload_filename(self, instance, filename):
        generator_klass = BaseDocumentFilenameGenerator.get(
            name=self.filename_generator_backend
        )
        generator_instance = generator_klass(
            **yaml_load(
                stream=self.filename_generator_backend_arguments or '{}'
            )
        )
        return generator_instance.upload_to(
            instance=instance, filename=filename
        )

    def new_document(
        self, file_object, label=None, description=None, language=None,
        user=None
    ):
        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        try:
            document = Document(
                description=description or '', document_type=self,
                label=label or file_object.name,
                language=language or setting_language.value
            )
            document._event_keep_attributes = ('_event_actor',)
            document._event_actor = user
            document.save()
        except Exception as exception:
            logger.critical(
                'Unexpected exception while trying to create new document '
                '"%s" from document type "%s"; %s',
                label or file_object.name, self, exception
            )
            raise
        else:
            try:
                document_file = document.file_new(
                    file_object=file_object, filename=label, user=user
                )
            except Exception as exception:
                logger.critical(
                    'Unexpected exception while trying to create initial '
                    'file for document %s; %s',
                    label or file_object.name, exception
                )
                document.delete(to_trash=False)
                raise
            else:
                return (document, document_file)
