from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from mayan.apps.sources.classes import DocumentCreateWizardStep
from mayan.apps.views.http import URL

from .forms import TagMultipleSelectionForm
from .models import Tag
from .permissions import permission_tag_attach


class DocumentCreateWizardStepTags(DocumentCreateWizardStep):
    form_class = TagMultipleSelectionForm
    label = _('Select tags')
    name = 'tag_selection'
    number = 2

    @classmethod
    def condition(cls, wizard):
        Tag = apps.get_model(app_label='tags', model_name='Tag')

        return Tag.objects.exists()

    @classmethod
    def get_form_kwargs(self, wizard):
        return {
            'help_text': _('Tags to be attached.'),
            'model': Tag,
            'permission': permission_tag_attach,
            'user': wizard.request.user
        }

    @classmethod
    def done(cls, wizard):
        result = {}
        cleaned_data = wizard.get_cleaned_data_for_step(cls.name)
        if cleaned_data:
            result['tags'] = [
                str(tag.pk) for tag in cleaned_data['tags']
            ]

        return result

    @classmethod
    def step_post_upload_process(
        cls, document, source_id, user_id, extra_data=None, query_string=None
    ):
        Tag = apps.get_model(app_label='tags', model_name='Tag')
        User = get_user_model()

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            user = None

        tag_id_list = URL(query_string=query_string).args.getlist('tags')

        for tag in Tag.objects.filter(pk__in=tag_id_list):
            if user:
                tag.attach_to(document=document, user=user)
            else:
                tag._attach_to(document=document)


DocumentCreateWizardStep.register(step=DocumentCreateWizardStepTags)
