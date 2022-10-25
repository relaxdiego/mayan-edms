from django.utils.translation import ugettext_lazy as _

DOCUMENT_FILE_DOWNLOAD_MESSAGE_BODY = _(
    'The document files have compressed '
    'and are available for download using the '
    'link: %(download_url)s or from '
    'the downloads area (%(download_list_url)s).'
)
DOCUMENT_FILE_DOWNLOAD_MESSAGE_SUBJECT = _(
    'Document files ready for download.'
)
