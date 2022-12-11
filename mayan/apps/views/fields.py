from django import forms

from .field_mixins import FilteredModelFieldMixin


class FilteredModelChoiceField(
    FilteredModelFieldMixin, forms.ModelChoiceField
):
    """Single selection filtered model choice field"""


class FilteredModelMultipleChoiceField(
    FilteredModelFieldMixin, forms.ModelMultipleChoiceField
):
    """Multiple selection filtered model choice field"""
