from mayan.apps.documents.tests.base import GenericDocumentViewTestCase

from .mixins import TransformationTestMixin, TransformationViewTestMixin


class TransformationLinkTestCase(
    TransformationTestMixin, TransformationViewTestMixin,
    GenericDocumentViewTestCase
):
    create_test_case_superuser = True
    create_test_case_user = False
    auto_login_superuser = True

    def test_transformation_link_view_with_super_user(self):
        self._create_test_transformation()

        self._clear_events()

        response = self._request_transformation_list_view()
        self.assertContains(
            response=response, text=str(self._test_transformation_object),
            status_code=200
        )
        self.assertContains(
            response=response,
            text=self._test_transformation.get_transformation_class().label,
            status_code=200
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
