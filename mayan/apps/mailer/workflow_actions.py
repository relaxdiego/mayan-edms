from django.utils.translation import ugettext_lazy as _

from mayan.apps.document_states.classes import WorkflowAction

from .literals import MODEL_SEND_FUNCTION_DOTTED_PATH
from .workflow_action_mixins import ObjectEmailActionMixin


class DocumentEmailAction(ObjectEmailActionMixin, WorkflowAction):
    fields = ObjectEmailActionMixin.fields.copy()
    fields.update(
        {
            'attachment': {
                'label': _('Attachment'),
                'class': 'django.forms.BooleanField', 'default': False,
                'help_text': _(
                    'Attach the exported document version to the email.'
                ),
                'required': False
            }
        }
    )
    field_order = list(
        ObjectEmailActionMixin.field_order
    ).append('attachment')
    label = _('Send document via email')
    previous_dotted_paths = (
        'mayan.apps.mailer.workflow_actions.EmailAction',
    )

    def get_execute_data(self, context):
        result = super().get_execute_data(context=context)
        document = self.get_object(context=context)

        if self.form_data.get('attachment', False):
            if document.version_active:
                # Document must have a version active in order to be able
                # to export and attach.
                obj = document.version_active
                result.update(
                    {
                        'as_attachment': True,
                        'obj': obj
                    }
                )
                result.update(
                    MODEL_SEND_FUNCTION_DOTTED_PATH.get(
                        obj._meta.model, {}
                    )
                )

        return result

    def get_object(self, context):
        return context['document']
