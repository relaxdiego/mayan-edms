from mayan.apps.events.classes import EventManagerMethodAfter
from mayan.apps.events.decorators import method_event

from .events import event_document_file_downloaded


@method_event(
    event_manager_class=EventManagerMethodAfter,
    event=event_document_file_downloaded,
    target='self'
)
def method_document_get_download_file_object(self):
    # Thin wrapper to make sure the normal views and API views trigger
    # then download event in the same way.
    return self.open(raw=True)
