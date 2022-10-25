from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.queues import queue_documents

queue_documents.add_task_type(
    dotted_path='mayan.apps.document_downloads.tasks.task_document_file_compress',
    label=_('Generate a compressed document file bundle')
)
