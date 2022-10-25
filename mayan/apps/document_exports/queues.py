from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.queues import queue_documents

queue_documents.add_task_type(
    dotted_path='mayan.apps.document_exports.tasks.task_document_version_export',
    label=_('Export a document version to a PDF')
)
