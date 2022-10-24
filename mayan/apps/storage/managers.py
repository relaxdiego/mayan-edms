from datetime import timedelta

from django.db import models
from django.utils.timezone import now

from .settings import (
    setting_download_file_expiration_interval,
    setting_shared_uploaded_file_expiration_interval
)


class DownloadFileManager(models.Manager):
    def stale(self):
        return self.filter(
            datetime__lt=now() - timedelta(
                seconds=setting_download_file_expiration_interval.value
            )
        )


class SharedUploadedFileManager(models.Manager):
    def stale(self):
        return self.filter(
            datetime__lt=now() - timedelta(
                seconds=setting_shared_uploaded_file_expiration_interval.value
            )
        )
