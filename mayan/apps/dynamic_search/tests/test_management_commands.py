from io import StringIO
from unittest import skip

from django.core import management

from mayan.apps.testing.tests.base import BaseTestCase
from mayan.apps.testing.tests.utils import mute_stdout

from ..search_backends import SearchBackend

from .mixins.backend_mixins import BackendSearchTestMixin
from .mixins.base import SearchTestMixin, TestSearchObjectSimpleTestMixin


class SearchReindexManagementCommandTestCaseMixin(
    BackendSearchTestMixin, SearchTestMixin, TestSearchObjectSimpleTestMixin
):
    def _call_command(self):
        with mute_stdout():
            management.call_command(command_name='search_reindex')

    def _create_test_search_objects(self):
        self._create_test_object(instance_kwargs={'char': 'abc'})

    def test_artifacts(self):
        self._test_search_backend.reset()

        queryset = self._do_search(
            query={'char': self._test_objects[0].char}
        )
        self.assertTrue(self._test_objects[0] not in queryset)

        self._call_command()

        queryset = self._do_search(
            query={'char': self._test_objects[0].char}
        )
        self.assertTrue(self._test_objects[0] in queryset)

    def test_calling(self):
        self._call_command()


class DjangoSearchReindexManagementCommandTestCase(
    SearchReindexManagementCommandTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.django.DjangoSearchBackend'
    """Test against Django backend."""

    @skip('Backend does not support reindexing.')
    def test_artifacts(self):
        """Backend does not support indexing."""


@skip('Skip until a Mock ElasticSearch server class is added.')
class ElasticSearchReindexManagementCommandTestCase(
    SearchReindexManagementCommandTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticSearchBackend'
    """Test against ElasticSearch backend."""


class WhooshSearchReindexManagementCommandTestCase(
    SearchReindexManagementCommandTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'
    """Test against Whoosh backend."""


class SearchIndexObjectManagementCommandTestCaseMixin(
    BackendSearchTestMixin, SearchTestMixin, TestSearchObjectSimpleTestMixin
):
    def _call_command(self, id_range_string):
        with mute_stdout():
            management.call_command(
                'search_index_objects',
                self._test_search_model.full_name, id_range_string
            )

    def _create_test_search_objects(self):
        self._create_test_object(instance_kwargs={'char': 'abc'})
        self._create_test_object(instance_kwargs={'char': 'xyz'})

    def test_artifacts(self):
        queryset = self._do_search(
            query={'char': self._test_objects[0].char}
        )
        self.assertTrue(self._test_objects[0] in queryset)

        queryset = self._do_search(
            query={'char': self._test_objects[1].char}
        )
        self.assertTrue(self._test_objects[1] in queryset)

        backend = SearchBackend.get_instance()
        backend.reset()

        queryset = self._do_search(
            query={'char': self._test_objects[0].char}
        )
        self.assertTrue(self._test_objects[0] not in queryset)

        queryset = self._do_search(
            query={'char': self._test_objects[1].char}
        )
        self.assertTrue(self._test_objects[1] not in queryset)

        self._call_command(id_range_string=self._test_objects[0].pk)

        queryset = self._do_search(
            query={'char': self._test_objects[0].char}
        )
        self.assertTrue(self._test_objects[0] in queryset)

        queryset = self._do_search(
            query={'char': self._test_objects[1].char}
        )
        self.assertTrue(self._test_objects[1] not in queryset)

        self._call_command(id_range_string=self._test_objects[1].pk)

        queryset = self._do_search(
            query={'char': self._test_objects[0].char}
        )
        self.assertTrue(self._test_objects[0] in queryset)

        queryset = self._do_search(
            query={'char': self._test_objects[1].char}
        )
        self.assertTrue(self._test_objects[1] in queryset)

    def test_calling(self):
        self._call_command(id_range_string=self._test_objects[0].pk)


class DjangoSearchIndexObjectManagementCommandTestCase(
    SearchIndexObjectManagementCommandTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.django.DjangoSearchBackend'
    """Test against Django backend."""

    @skip('Backend does not support indexing.')
    def test_artifacts(self):
        """Backend does not support indexing."""


@skip('Skip until a Mock ElasticSearch server class is added.')
class ElasticSearchIndexObjectManagementCommandTestCase(
    SearchIndexObjectManagementCommandTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticSearchBackend'
    """Test against ElasticSearch backend."""


class WhooshSearchIndexObjectManagementCommandTestCase(
    SearchIndexObjectManagementCommandTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'
    """Test against Whoosh backend."""


class SearchStatusManagementCommandTestCaseMixin(
    SearchTestMixin, TestSearchObjectSimpleTestMixin
):
    def _create_test_search_objects(self):
        self._create_test_object(instance_kwargs={'char': 'abc'})
        self._create_test_object(instance_kwargs={'char': 'xyz'})

    def test_artifacts(self):
        output = StringIO()
        options = {
            'stdout': output
        }

        management.call_command(command_name='search_status', **options)
        output.seek(0)

        count = 0

        lines = output.readlines()
        for line in lines:
            if self._test_search_model.model_name in line.lower():
                model_name, count = line.split(':')
                count = int(count)

        self.assertEqual(count, len(self._test_objects))


class DjangoSearchStatusManagementCommandTestCase(
    SearchStatusManagementCommandTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.django.DjangoSearchBackend'
    """Test against DjangoSearch backend."""


@skip('Skip until a Mock ElasticSearch server class is added.')
class ElasticSearchStatusManagementCommandTestCase(
    SearchStatusManagementCommandTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticSearchBackend'
    """Test against ElasticSearch backend."""


class WhooshSearchStatusManagementCommandTestCase(
    SearchStatusManagementCommandTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'
    """Test against WhooshSearch backend."""
