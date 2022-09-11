from ..document_file_actions import (
    DocumentFileActionAppendNewPages, DocumentFileActionNothing,
    DocumentFileActionUseNewPages
)

from .base import GenericDocumentTestCase
from .mixins.document_file_mixins import DocumentFileTestMixin


class DocumentVersionTestCase(
    DocumentFileTestMixin, GenericDocumentTestCase
):
    def test_version_new_file_new_pages(self):
        test_document_version_page_content_objects = self._test_document_version.page_content_objects

        self.assertEqual(self._test_document.versions.count(), 1)

        self._upload_test_document_file(
            action=DocumentFileActionUseNewPages.backend_id
        )

        self.assertEqual(self._test_document.versions.count(), 2)

        self.assertNotEqual(
            self._test_document_version.page_content_objects,
            test_document_version_page_content_objects
        )
        self.assertEqual(
            self._test_document_version.page_content_objects,
            list(self._test_document.file_latest.pages.all())
        )

    def test_version_new_version_keep_pages(self):
        test_document_version_page_content_objects = self._test_document_version.page_content_objects

        self.assertEqual(self._test_document.versions.count(), 1)

        self._upload_test_document_file(
            action=DocumentFileActionNothing.backend_id
        )

        self.assertEqual(self._test_document.versions.count(), 1)

        self.assertEqual(
            self._test_document_version.page_content_objects,
            test_document_version_page_content_objects
        )
        self.assertNotEqual(
            self._test_document_version.page_content_objects,
            list(self._test_document.file_latest.pages.all())
        )

    def test_version_new_file_append_pages(self):
        test_document_version_page_content_objects = self._test_document_version.page_content_objects

        self.assertEqual(self._test_document.versions.count(), 1)
        self.assertEqual(self._test_document.files.count(), 1)

        self._upload_test_document_file(
            action=DocumentFileActionAppendNewPages.backend_id
        )

        self.assertEqual(self._test_document.files.count(), 2)
        self.assertEqual(self._test_document.versions.count(), 2)

        test_document_version_expected_page_content_objects = list(
            self._test_document.files.first().pages.all()
        )
        test_document_version_expected_page_content_objects.extend(
            list(
                self._test_document.files.last().pages.all()
            )
        )

        self.assertNotEqual(
            self._test_document_version.page_content_objects,
            test_document_version_page_content_objects
        )
        self.assertEqual(
            self._test_document_version.page_content_objects,
            test_document_version_expected_page_content_objects
        )

    def test_method_get_absolute_url(self):
        self.assertTrue(
            self._test_document.version_active.get_absolute_url()
        )
