from unittest import skip

from mayan.apps.testing.tests.base import BaseTestCase

from ..exceptions import DynamicSearchBackendException
from ..search_query_types import QueryTypeExact

from .mixins.base import SearchTestMixin, TestSearchObjectSimpleTestMixin
from .mixins.backend_mixins import BackendSearchTestMixin
from .mixins.backend_search_field_mixins import BackendSearchFieldTestCaseMixin
from .mixins.backend_query_type_mixins import BackendFieldTypeQueryTypeTestCaseMixin


class DjangoSearchBackendSearchFieldTestCase(
    BackendSearchFieldTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.django.DjangoSearchBackend'


class DjangoSearchBackendFieldTypeQueryTypeTestCase(
    BackendFieldTypeQueryTypeTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.django.DjangoSearchBackend'

    @skip('Backend does not support the feature.')
    def test_search_field_type_char_search_exact_accent(self):
        """
        This backend does not require indexing which is required
        for this feature to work.
        """

    @skip('Backend does not support the feature.')
    def test_search_field_type_char_search_fuzzy(self):
        """
        This query type is emulated and does not return the same results
        as backends support this natively.
        """

    @skip('Backend does not support the feature.')
    def test_search_field_type_text_search_fuzzy(self):
        """
        This query type is emulated and does not return the same results
        as backends support this natively.
        """


@skip('Skip until a Mock ElasticSearch server class is added.')
class ElasticSearchBackendIndexingTestCase(
    BackendSearchTestMixin, TestSearchObjectSimpleTestMixin, SearchTestMixin,
    BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticSearchBackend'

    def test_search_without_indexes(self):
        self._test_search_backend.tear_down()

        with self.assertRaises(expected_exception=DynamicSearchBackendException):
            self._do_backend_search(
                field_name='char',
                query_type=QueryTypeExact,
                value=self._test_object.char,
                _skip_refresh=True,
            )


@skip('Skip until a Mock ElasticSearch server class is added.')
class ElasticSearchBackendSearchFieldTestCase(
    BackendSearchFieldTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticSearchBackend'


@skip('Skip until a Mock ElasticSearch server class is added.')
class ElasticSearchBackendFieldTypeQueryTypeTestCase(
    BackendFieldTypeQueryTypeTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.elasticsearch.ElasticSearchBackend'


class WhooshSearchBackendSearchFieldTestCase(
    BackendSearchFieldTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'


class WhooshSearchBackendFieldTypeQueryTypeTestCase(
    BackendFieldTypeQueryTypeTestCaseMixin, BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'


class WhooshSearchBackendSpecificTestCase(
    BackendSearchTestMixin, TestSearchObjectSimpleTestMixin, SearchTestMixin,
    BaseTestCase
):
    _test_search_backend_path = 'mayan.apps.dynamic_search.backends.whoosh.WhooshSearchBackend'

    def test_whoosh_datetime_search_raw_parsed_date_human_today(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            is_raw_value=True,
            query_type=QueryTypeExact,
            value='today'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_whoosh_datetime_search_raw_parsed_date_human_range(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            is_raw_value=True,
            query_type=QueryTypeExact,
            value='[\'last tuesday\' to \'next friday\']'
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_whoosh_datetime_search_raw_parsed_date_numeric_range(self):
        id_list = self._do_backend_search(
            field_name='datetime',
            is_raw_value=True,
            query_type=QueryTypeExact,
            value='[\'{}\' to \'{}\']'.format(
                self._test_object.datetime.year - 1,
                self._test_object.datetime.year + 1
            )
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)

    def test_whoosh_integer_search_raw_parsed_numeric_range(self):
        id_list = self._do_backend_search(
            field_name='integer',
            is_raw_value=True,
            query_type=QueryTypeExact,
            value='[\'{}\' to \'{}\']'.format(
                self._test_object.integer - 1,
                self._test_object.integer + 1
            )
        )

        self.assertEqual(len(id_list), 1)
        self.assertTrue(self._test_object.id in id_list)
