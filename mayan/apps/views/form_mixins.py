from django import forms as django_forms
from django.utils.module_loading import import_string


class DynamicFormMixin:
    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop('schema')
        super().__init__(*args, **kwargs)

        widgets = self.schema.get(
            'widgets', {}
        )
        field_order = self.schema.get(
            'field_order', self.schema['fields'].keys()
        )

        for field_name in field_order:
            field_data = self.schema['fields'][field_name]
            field_class = import_string(
                dotted_path=field_data['class']
            )
            kwargs = {
                'label': field_data['label'],
                'required': field_data.get('required', True),
                'initial': field_data.get('default', None),
                'help_text': field_data.get('help_text')
            }
            if widgets and field_name in widgets:
                widget = widgets[field_name]
                kwargs['widget'] = import_string(
                    dotted_path=widget['class']
                )(
                    **widget.get(
                        'kwargs', {}
                    )
                )

            kwargs.update(
                field_data.get(
                    'kwargs', {}
                )
            )
            self.fields[field_name] = field_class(**kwargs)

    @property
    def media(self):
        """
        Append the media of the dynamic fields to the normal fields' media.
        """
        media = super().media
        media += django_forms.Media(
            **self.schema.get(
                'media', {}
            )
        )
        return media


class FormFieldsetMixin:
    fieldsets = None

    def get_fieldsets(self):
        if self.fieldsets:
            return self.fieldsets
        else:
            return (
                (
                    None, {
                        'fields': tuple(self.fields)
                    }
                ),
            )
