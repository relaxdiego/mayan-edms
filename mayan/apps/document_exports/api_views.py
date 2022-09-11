from rest_framework import status

from mayan.apps.rest_api import generics
from mayan.apps.documents.api_views.mixins import (
    ParentObjectDocumentAPIViewMixin
)

from .permissions import permission_document_version_export
from .tasks import task_document_version_export


class APIDocumentVersionExportView(
    ParentObjectDocumentAPIViewMixin, generics.ObjectActionAPIView
):
    """
    post: Exports the specified document version.
    """
    action_response_status = status.HTTP_202_ACCEPTED
    lookup_url_kwarg = 'document_version_id'
    mayan_object_permissions = {
        'POST': (permission_document_version_export,),
    }

    def get_queryset(self):
        return self.get_document().versions.all()

    def object_action(self, request, serializer):
        task_document_version_export.apply_async(
            kwargs={
                'document_version_id': self.object.pk,
                'user_id': request.user.id
            }
        )
