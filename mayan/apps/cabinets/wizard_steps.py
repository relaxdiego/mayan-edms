from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from mayan.apps.sources.classes import DocumentCreateWizardStep
from mayan.apps.views.http import URL

from .forms import CabinetListForm
from .models import Cabinet
from .permissions import permission_cabinet_add_document


class DocumentCreateWizardStepCabinets(DocumentCreateWizardStep):
    form_class = CabinetListForm
    label = _('Select cabinets')
    name = 'cabinet_selection'
    number = 3

    @classmethod
    def condition(cls, wizard):
        Cabinet = apps.get_model(
            app_label='cabinets', model_name='Cabinet'
        )
        return Cabinet.objects.exists()

    @classmethod
    def get_form_kwargs(self, wizard):
        return {
            'help_text': _('Cabinets to which the document will be added.'),
            'permission': permission_cabinet_add_document,
            'queryset': Cabinet.objects.all(),
            'user': wizard.request.user
        }

    @classmethod
    def done(cls, wizard):
        result = {}
        cleaned_data = wizard.get_cleaned_data_for_step(step=cls.name)
        if cleaned_data:
            result['cabinets'] = [
                str(cabinet.pk) for cabinet in cleaned_data['cabinets']
            ]

        return result

    @classmethod
    def step_post_upload_process(
        cls, document, source_id, user_id, extra_data=None, query_string=None
    ):
        Cabinet = apps.get_model(app_label='cabinets', model_name='Cabinet')
        User = get_user_model()

        cabinet_id_list = URL(
            query_string=query_string
        ).args.getlist('cabinets')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            user = None

        for cabinet in Cabinet.objects.filter(pk__in=cabinet_id_list):
            if user:
                cabinet.document_add(document=document, user=user)
            else:
                cabinet._document_add(document=document)


DocumentCreateWizardStep.register(DocumentCreateWizardStepCabinets)
