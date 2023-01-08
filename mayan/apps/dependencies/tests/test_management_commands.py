from unittest import mock

import mayan

from mayan.apps.common.tests.mixins import ManagementCommandTestMixin
from mayan.apps.testing.tests.base import BaseTestCase

from ..literals import (
    COMMAND_NAME_DEPENDENCIES_CHECK_VERSION,
    COMMAND_NAME_DEPENDENCIES_SHOW_VERSION
)
from ..utils import (
    MESSAGE_NOT_LATEST, MESSAGE_UNKNOWN_VERSION, MESSAGE_UP_TO_DATE
)


class CheckVersionManagementCommandTestCase(
    ManagementCommandTestMixin, BaseTestCase
):
    _test_management_command_name = COMMAND_NAME_DEPENDENCIES_CHECK_VERSION

    @mock.patch('mayan.apps.dependencies.utils.PyPIClient.get_versions', autospec=True)
    def test_check_version_not_latest_version(self, mock_package_releases):
        mock_package_releases.return_value = ('0.0.0',)
        stdout, stderr = self._call_test_management_command()
        self.assertTrue(
            stdout.startswith(
                MESSAGE_NOT_LATEST[:-2]
            )
        )

    @mock.patch('mayan.apps.dependencies.utils.PyPIClient.get_versions', autospec=True)
    def test_check_version_unknown_version(self, mock_package_releases):
        mock_package_releases.return_value = None
        stdout, stderr = self._call_test_management_command()
        self.assertTrue(
            stdout.startswith(MESSAGE_UNKNOWN_VERSION)
        )

    @mock.patch('mayan.apps.dependencies.utils.PyPIClient.get_versions', autospec=True)
    def test_check_version_correct_version(self, mock_package_releases):
        mock_package_releases.return_value = (mayan.__version__,)
        stdout, stderr = self._call_test_management_command()
        self.assertTrue(
            stdout.startswith(MESSAGE_UP_TO_DATE)
        )


class ShowVersionManagementCommandTestCase(
    ManagementCommandTestMixin, BaseTestCase
):
    _test_management_command_name = COMMAND_NAME_DEPENDENCIES_SHOW_VERSION
    create_test_case_user = False

    def test_version_command_base(self):
        stdout, stderr = self._call_test_management_command()
        self.assertIn(
            mayan.__version__, stdout
        )

    def test_version_command_build_string(self):
        stdout, stderr = self._call_test_management_command(build_string=True)
        self.assertIn(
            mayan.__build_string__, stdout
        )
