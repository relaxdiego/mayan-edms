import logging
from pathlib import Path

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.files import File

from mayan.apps.converter.layers import layer_saved_transformations
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.tasks import task_document_upload
from mayan.apps.storage.compressed_files import Archive
from mayan.apps.storage.exceptions import NoMIMETypeMatch
from mayan.apps.storage.models import SharedUploadedFile

logger = logging.getLogger(name=__name__)


class SourceBusinessLogicMixin:
    @staticmethod
    def callback_post_task_document_upload(document_file, **kwargs):
        Source = apps.get_model(app_label='sources', model_name='Source')

        source = Source.objects.get(
            pk=kwargs['source_id']
        )

        if kwargs['user_id']:
            User = get_user_model()
            try:
                user = User.objects.get(
                    pk=kwargs['user_id']
                )
            except User.DoesNotExist:
                """Skip adding recent document."""
            else:
                document_file.document.add_as_recent_document_for_user(
                    user=user
                )

        layer_saved_transformations.copy_transformations(
            source=source, targets=document_file.pages.all()
        )

        source.get_backend_instance().callback(
            document_file=document_file, **kwargs
        )

    def execute_action(self, name, **kwargs):
        return self.get_backend_instance().execute_action(
            name=name, **kwargs
        )

    def fullname(self):
        return '{} {}'.format(
            self.get_backend_label(), self.label
        )

    def get_action(self, name):
        return self.get_backend().get_action(name=name)

    def get_actions(self):
        return self.get_backend().get_actions()

    def handle_file_object_upload(
        self, document_type, file_object, callback_kwargs=None,
        description=None, expand=False, label=None, language=None, user=None
    ):
        """
        Handle an upload request from a file object which may be an individual
        document or a compressed file containing multiple documents.
        """
        callback_kwargs = callback_kwargs or {}

        if expand:
            try:
                compressed_file = Archive.open(file_object=file_object)
                for compressed_file_member in compressed_file.members():
                    with compressed_file.open_member(filename=compressed_file_member) as compressed_file_member_file_object:
                        # Recursive call to expand nested compressed files
                        # expand=True literal for recursive nested files.
                        # Might cause problem with office files inside a
                        # compressed file.
                        self.handle_file_object_upload(
                            callback_kwargs=callback_kwargs,
                            document_type=document_type,
                            description=description,
                            expand=False,
                            file_object=compressed_file_member_file_object,
                            # Use the filename only and not the whole path.
                            label=Path(compressed_file_member).name,
                            language=language,
                            user=user
                        )

                # Avoid executing the expand=False code path.
                return
            except NoMIMETypeMatch:
                logger.debug(msg='No expanding; Exception: NoMIMETypeMatch')
                # Fallthrough to same code path as expand=False to avoid
                # duplicating code.

        shared_uploaded_file = SharedUploadedFile.objects.create(
            file=File(file_object)
        )

        Document.execute_pre_create_hooks(
            kwargs={
                'document_type': document_type,
                'user': user
            }
        )

        if user:
            user_id = user.pk
        else:
            user_id = None

        final_callback_kwargs = callback_kwargs.copy()
        final_callback_kwargs.update(
            {
                'source_id': self.pk,
                'user_id': user_id
            }
        )

        task_document_upload.apply_async(
            kwargs={
                'callback_dotted_path': 'mayan.apps.sources.models.Source',
                'callback_function': 'callback_post_task_document_upload',
                'callback_kwargs': final_callback_kwargs,
                'description': description,
                'document_type_id': document_type.pk,
                'label': label,
                'language': language,
                'shared_uploaded_file_id': shared_uploaded_file.pk,
                'user_id': user_id
            }
        )
