from __future__ import unicode_literals

import datetime

from django.test import override_settings
from django.utils.encoding import force_text
from django.utils.timezone import now

from rest_framework import status

from documents.models import DocumentType
from documents.tests import TEST_DOCUMENT_TYPE_LABEL, TEST_SMALL_DOCUMENT_PATH
from documents.permissions import permission_document_view
from rest_api.tests import BaseAPITestCase

from ..models import DocumentCheckout
from ..permissions import permission_document_checkout_detail_view


@override_settings(OCR_AUTO_OCR=False)
class CheckoutsAPITestCase(BaseAPITestCase):
    def setUp(self):
        super(CheckoutsAPITestCase, self).setUp()
        self.login_user()
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

        with open(TEST_SMALL_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object,
            )

    def tearDown(self):
        self.document_type.delete()
        super(CheckoutsAPITestCase, self).tearDown()

    def _request_checkedout_document_view(self):
        return self.get(
            viewname='rest_api:checkedout-document-view',
            args=(self.document.pk,)
        )

    def _checkout_document(self):
        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self.admin_user, block_new_version=True
        )

    def test_checkedout_document_view_no_access(self):
        response = self._request_checkedout_document_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkedout_document_view_with_checkout_access(self):
        self._checkout_document()
        self.grant_access(
            permission=permission_document_checkout_detail_view, obj=self.document
        )
        response = self._request_checkedout_document_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkedout_document_view_with_document_access(self):
        self._checkout_document()
        self.grant_access(
            permission=permission_document_view, obj=self.document
        )
        response = self._request_checkedout_document_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkedout_document_view_with_access(self):
        self._checkout_document()
        self.grant_access(
            permission=permission_document_view, obj=self.document
        )
        self.grant_access(
            permission=permission_document_checkout_detail_view, obj=self.document
        )
        response = self._request_checkedout_document_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['document']['uuid'], force_text(self.document.uuid))
