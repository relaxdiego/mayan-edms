from django import forms
from django.utils.translation import ugettext_lazy as _

from .literals import MATCH_ALL_FIELD_CHOICES, MATCH_ALL_FIELD_NAME


class AdvancedSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs['data'] = kwargs['data'].copy()
        self.search_model = kwargs.pop('search_model')
        super().__init__(*args, **kwargs)

        self.fields[MATCH_ALL_FIELD_NAME] = forms.ChoiceField(
            choices=MATCH_ALL_FIELD_CHOICES, widget=forms.RadioSelect,
            label=_('Match all'), help_text=_(
                'Return only results that match all fields.'
            ), required=False
        )

        for search_field in self.search_model.search_fields:
            if search_field.concrete:
                self.fields[search_field.field_name] = forms.CharField(
                    help_text=search_field.get_help_text(),
                    label=search_field.label, required=False,
                    widget=forms.widgets.TextInput(attrs={'type': 'search'})
                )


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=128, label=_('Search terms'), required=False,
        widget=forms.widgets.TextInput(attrs={'type': 'search'})
    )
