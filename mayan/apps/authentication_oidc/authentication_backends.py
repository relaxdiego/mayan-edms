from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.authentication.classes import AuthenticationBackend

from mayan.apps.common.utils import get_class_full_name

from .django_authentication_backends import DjangoAuthenticationBackendOIDC
from .forms import AuthenticationFormOIDC


class AuthenticationBackendOIDC(AuthenticationBackend):
    login_form_class = AuthenticationFormOIDC

    def __init__(self, **kwargs):
        super().__init__()

    def initialize(self):
        settings.AUTHENTICATION_BACKENDS = (
            get_class_full_name(klass=DjangoAuthenticationBackendOIDC),
        )

        settings.MIDDLEWARE += ('mozilla_django_oidc.middleware.SessionRefresh',)

        settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
            'mozilla_django_oidc.contrib.drf.OIDCAuthentication',
        ) + settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']

    def get_context_data(self):
        return {
            'form_action': reverse(viewname='oidc_authentication_init'),
            'submit_button_css_extra_classes': 'center-block',
            'submit_label': _('Login via OIDC'),
            'submit_method': 'get'
        }
