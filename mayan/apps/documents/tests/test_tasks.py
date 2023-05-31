from unittest import mock

from django.core.files import File

from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.testing.tests.base import BaseTestCase

from ..events import (
    event_document_created, event_document_file_created,
    event_document_file_edited, event_document_version_created,
    event_document_version_page_created
)
from ..models.document_models import Document
from ..tasks import task_document_upload

from .mixins.document_mixins import DocumentTestMixin


class DocumentTaskTestCase(DocumentTestMixin, BaseTestCase):
    auto_upload_test_document = False

    @staticmethod
    def _test_callback(document_file, test_argument):
        return test_argument

    def test_task_document_upload(self):
        self._calculate_test_document_path()

        with open(file=self.test_document_path, mode='rb') as file_object:
            test_shared_uploaded_file = SharedUploadedFile.objects.create(
                file=File(file=file_object)
            )

        self._clear_events()

        task_document_upload.apply_async(
            kwargs={
                'document_type_id': self.test_document_type.pk,
                'shared_uploaded_file_id': test_shared_uploaded_file.pk,
                'user_id': self._test_case_user.pk
            }
        )

        self.test_document = Document.objects.first()
        self.test_document_file = self.test_document.file_latest
        self.test_document_version = self.test_document.version_active
        self.test_document_version_page = self.test_document_version.pages.first()

        events = self._get_test_events()
        self.assertEqual(events.count(), 5)

        # Document created

        self.assertEqual(events[0].action_object, self.test_document_type)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self.test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        # Document file created

        self.assertEqual(events[1].action_object, self.test_document)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].target, self.test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        # Document file edited (MIME type, page count update)

        self.assertEqual(events[2].action_object, self.test_document)
        self.assertEqual(events[2].actor, self._test_case_user)
        self.assertEqual(events[2].target, self.test_document_file)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        # Document version created

        self.assertEqual(events[3].action_object, self.test_document)
        self.assertEqual(events[3].actor, self._test_case_user)
        self.assertEqual(
            events[3].target, self.test_document.version_active
        )
        self.assertEqual(events[3].verb, event_document_version_created.id)

        # Document version page created

        self.assertEqual(
            events[4].action_object, self.test_document_version
        )
        self.assertEqual(events[4].actor, self._test_case_user)
        self.assertEqual(
            events[4].target, self.test_document_version_page
        )
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )

    @mock.patch(target='mayan.apps.documents.tests.test_tasks.DocumentTaskTestCase._test_callback')
    def test_task_document_upload_callback(self, mocked_callback):
        self._calculate_test_document_path()

        with open(file=self.test_document_path, mode='rb') as file_object:
            test_shared_uploaded_file = SharedUploadedFile.objects.create(
                file=File(file=file_object)
            )

        self._clear_events()

        task_document_upload.apply_async(
            kwargs={
                'document_type_id': self.test_document_type.pk,
                'shared_uploaded_file_id': test_shared_uploaded_file.pk,
                'user_id': self._test_case_user.pk,
                'callback_dotted_path': 'mayan.apps.documents.tests.test_tasks.DocumentTaskTestCase',
                'callback_function': '_test_callback',
                'callback_kwargs': {'test_argument': 'test_value'}
            }
        )

        self.test_document = Document.objects.first()
        self.test_document_file = self.test_document.file_latest
        self.test_document_version = self.test_document.version_active
        self.test_document_version_page = self.test_document_version.pages.first()

        self.assertEqual(mocked_callback.call_count, 1)
        mocked_callback.assert_called_with(
            document_file=self.test_document_file, test_argument='test_value'
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 5)

        # Document created

        self.assertEqual(events[0].action_object, self.test_document_type)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self.test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        # Document file created

        self.assertEqual(events[1].action_object, self.test_document)
        self.assertEqual(events[1].actor, self._test_case_user)
        self.assertEqual(events[1].target, self.test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        # Document file edited (MIME type, page count update)

        self.assertEqual(events[2].action_object, self.test_document)
        self.assertEqual(events[2].actor, self._test_case_user)
        self.assertEqual(events[2].target, self.test_document_file)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        # Document version created

        self.assertEqual(events[3].action_object, self.test_document)
        self.assertEqual(events[3].actor, self._test_case_user)
        self.assertEqual(
            events[3].target, self.test_document.version_active
        )
        self.assertEqual(events[3].verb, event_document_version_created.id)

        # Document version page created

        self.assertEqual(
            events[4].action_object, self.test_document_version
        )
        self.assertEqual(events[4].actor, self._test_case_user)
        self.assertEqual(
            events[4].target, self.test_document_version_page
        )
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )
