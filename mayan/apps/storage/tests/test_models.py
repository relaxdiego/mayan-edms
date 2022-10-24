from django.urls import reverse

from mayan.apps.testing.tests.base import BaseTestCase

from ..models import DownloadFile, SharedUploadedFile
from ..settings import (
    setting_download_file_expiration_interval,
    setting_shared_uploaded_file_expiration_interval
)

from .mixins import DownloadFileTestMixin, SharedUploadedFileTestMixin


class DownloadFileModelTestCase(DownloadFileTestMixin, BaseTestCase):
    def test_download_file_expiration(self):
        setting_download_file_expiration_interval.set(value=60)
        self._create_test_download_file()

        self.assertEqual(DownloadFile.objects.stale().count(), 0)

        setting_download_file_expiration_interval.set(value=0)

        self.assertEqual(DownloadFile.objects.stale().count(), 1)

    def test_method_get_absolute_url(self):
        self._create_test_download_file()

        self.assertEqual(
            self.test_download_file.get_absolute_url(),
            reverse(viewname='storage:download_file_list')
        )


class SharedUploadedFileManagerTestCase(
    SharedUploadedFileTestMixin, BaseTestCase
):
    def test_shared_uploaded_expiration(self):
        setting_shared_uploaded_file_expiration_interval.set(value=60)
        self._create_test_shared_uploaded_file()

        self.assertEqual(SharedUploadedFile.objects.stale().count(), 0)

        setting_shared_uploaded_file_expiration_interval.set(value=0)

        self.assertEqual(SharedUploadedFile.objects.stale().count(), 1)
