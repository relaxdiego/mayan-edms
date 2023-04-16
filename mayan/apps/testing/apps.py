from django.core import checks
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig

from .checks import check_app_tests


class TestingApp(MayanAppConfig):
    name = 'mayan.apps.testing'
    verbose_name = _('Testing')

    def ready(self, *args, **kwargs):
        super().ready(*args, **kwargs)

        checks.register(check=check_app_tests)
