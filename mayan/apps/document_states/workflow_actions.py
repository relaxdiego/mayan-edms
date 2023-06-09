import logging
import json

import requests

from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _

from .classes import WorkflowAction
from .exceptions import WorkflowStateActionError
from .literals import (
    BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT,
    DEFAULT_HTTP_ACTION_TIMEOUT
)
from .models.workflow_instance_models import WorkflowInstance
from .models.workflow_models import Workflow
from .tasks import task_launch_workflow_for

logger = logging.getLogger(name=__name__)


class DocumentPropertiesEditAction(WorkflowAction):
    fields = {
        'document_label': {
            'label': _('Document label'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _('The new label to be assigned to the document.'),
                        BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            },
        }, 'document_description': {
            'label': _('Document description'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _(
                            'The new description to be assigned to the '
                            'document.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            }
        }
    }
    field_order = ('document_label', 'document_description')
    label = _('Modify document properties')

    def execute(self, context):
        self.document_label = self.form_data.get('document_label')
        self.document_description = self.form_data.get(
            'document_description'
        )
        new_label = None
        new_description = None

        if self.document_label:
            new_label = self.render_field(
                field_name='document_label', context=context
            )

        if self.document_description:
            new_description = self.render_field(
                field_name='document_description', context=context
            )

        if new_label or new_description:
            document = context['document']
            document.label = new_label or document.label
            document.description = new_description or document.description

            document.save()


class DocumentWorkflowLaunchAction(WorkflowAction):
    fields = {
        'workflows': {
            'label': _('Workflows'),
            'class': 'django.forms.ModelMultipleChoiceField', 'kwargs': {
                'help_text': _(
                    'Additional workflows to launch for the document.'
                ), 'queryset': Workflow.objects.none()
            },
        },
    }
    field_order = ('workflows',)
    label = _('Launch workflows')
    widgets = {
        'workflows': {
            'class': 'django.forms.widgets.SelectMultiple', 'kwargs': {
                'attrs': {'class': 'select2'},
            }
        }
    }

    def get_form_schema(self, **kwargs):
        result = super().get_form_schema(**kwargs)

        workflows_union = Workflow.objects.filter(
            document_types__in=kwargs['workflow_state'].workflow.document_types.all()
        ).exclude(pk=kwargs['workflow_state'].workflow.pk).distinct()

        result['fields']['workflows']['kwargs']['queryset'] = workflows_union

        return result

    def execute(self, context):
        workflows = Workflow.objects.filter(
            pk__in=self.form_data.get('workflows', ())
        )

        for workflow in workflows:
            task_launch_workflow_for.apply_async(
                kwargs={
                    'document_id': context['document'].pk,
                    'workflow_id': workflow.pk
                }
            )


class HTTPAction(WorkflowAction):
    fields = {
        'url': {
            'label': _('URL'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _('The URL to access.'),
                        BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': True
            },
        }, 'timeout': {
            'label': _('Timeout'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'default': DEFAULT_HTTP_ACTION_TIMEOUT,
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _('Time in seconds to wait for a response.'),
                        BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': True
            }
        }, 'payload': {
            'label': _('Payload'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _('A JSON document to include in the request.'),
                        BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            }
        }, 'username': {
            'label': _('Username'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _(
                            'Username to use for making the request with '
                            'HTTP Basic Auth.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'max_length': 192,
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            },
        }, 'password': {
            'label': _('Password'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _(
                            'Password to use for making the request with '
                            'HTTP Basic Auth.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'max_length': 192,
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            },
        }, 'method': {
            'label': _('Method'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _(
                            'The HTTP method to use for the request. '
                            'Typical choices are OPTIONS, HEAD, POST, GET, '
                            'PUT, PATCH, DELETE.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': True
            }
        }, 'headers': {
            'label': _('Headers'),
            'class': 'mayan.apps.templating.fields.ModelTemplateField',
            'kwargs': {
                'initial_help_text': _(
                    format_lazy(
                        '{} {}',
                        _(
                            'Headers to send with the HTTP request. Must '
                            'be in JSON format.'
                        ), BASE_WORKFLOW_TEMPLATE_STATE_ACTION_HELP_TEXT
                    )
                ),
                'model': WorkflowInstance,
                'model_variable': 'workflow_instance',
                'required': False
            }
        }
    }
    field_order = (
        'url', 'username', 'password', 'headers', 'timeout', 'method',
        'payload'
    )
    label = _('Perform an HTTP request')
    previous_dotted_paths = (
        'mayan.apps.document_states.workflow_actions.HTTPPostAction',
    )

    def render_field_load(self, field_name, context):
        """
        Method to perform a template render and subsequent JSON load.
        """
        render_result = self.render_field(
            field_name=field_name, context=context
        ) or '{}'

        try:
            load_result = json.loads(s=render_result, strict=False)
        except Exception as exception:
            raise WorkflowStateActionError(
                _('%(field_name)s JSON error: %(exception)s') % {
                    'field_name': field_name, 'exception': exception
                }
            )

        logger.debug('load result: %s', load_result)

        return load_result

    def execute(self, context):
        headers = self.render_field_load(
            field_name='headers', context=context
        )
        method = self.render_field(field_name='method', context=context)
        password = self.render_field(field_name='password', context=context)
        payload = self.render_field_load(
            field_name='payload', context=context
        )
        timeout = self.render_field(field_name='timeout', context=context)
        url = self.render_field(field_name='url', context=context)
        username = self.render_field(field_name='username', context=context)

        if '.' in timeout:
            timeout = float(timeout)
        elif timeout:
            timeout = int(timeout)
        else:
            timeout = None

        authentication = None
        if username or password:
            authentication = requests.auth.HTTPBasicAuth(
                password=password, username=username
            )

        requests.request(
            auth=authentication, headers=headers, json=payload,
            method=method, timeout=timeout, url=url
        )
