from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

from .literals import (
    DEFAULT_AUTHENTICATION_OIDC_USER_PROFILE_URL,
    DEFAULT_OIDC_OP_AUTHORIZATION_ENDPOINT, DEFAULT_OIDC_OP_JWKS_ENDPOINT,
    DEFAULT_OIDC_OP_TOKEN_ENDPOINT, DEFAULT_OIDC_OP_USER_ENDPOINT,
    DEFAULT_OIDC_RP_CLIENT_ID, DEFAULT_OIDC_RP_CLIENT_SECRET,
    DEFAULT_OIDC_RP_SIGN_ALGO, DEFAULT_OIDC_USERNAME_ALGO
)

namespace = SettingNamespace(
    label=_('Mozilla Django OIDC'), name='mozilla_django_oidc'
)

setting_oidc_op_authorization_endpoint = namespace.add_setting(
    default=DEFAULT_OIDC_OP_AUTHORIZATION_ENDPOINT,
    global_name='OIDC_OP_AUTHORIZATION_ENDPOINT', help_text=_(
        'URL of your OpenID Connect provider authorization endpoint.'
    )
)
setting_oidc_op_jwks_endpoint = namespace.add_setting(
    default=DEFAULT_OIDC_OP_JWKS_ENDPOINT, global_name='OIDC_OP_JWKS_ENDPOINT'
)
setting_oidc_op_token_endpoint = namespace.add_setting(
    default=DEFAULT_OIDC_OP_TOKEN_ENDPOINT,
    global_name='OIDC_OP_TOKEN_ENDPOINT', help_text=_(
        'URL of your OpenID Connect provider token endpoint.'
    )
)
setting_oidc_op_user_endpoint = namespace.add_setting(
    default=DEFAULT_OIDC_OP_USER_ENDPOINT,
    global_name='OIDC_OP_USER_ENDPOINT', help_text=_(
        'URL of your OpenID Connect provider userinfo endpoint.'
    )
)

setting_oidc_rp_client_id = namespace.add_setting(
    default=DEFAULT_OIDC_RP_CLIENT_ID, global_name='OIDC_RP_CLIENT_ID',
    help_text=_(
        'OpenID Connect client ID provided by your OP.'
    )
)
setting_oidc_rp_client_secret = namespace.add_setting(
    default=DEFAULT_OIDC_RP_CLIENT_SECRET,
    global_name='OIDC_RP_CLIENT_SECRET', help_text=_(
        'OpenID Connect client secret provided by your OP'
    )
)
setting_oidc_rp_sign_algo = namespace.add_setting(
    default=DEFAULT_OIDC_RP_SIGN_ALGO, global_name='OIDC_RP_SIGN_ALGO',
    help_text=_('Sets the algorithm the IdP uses to sign ID tokens.')
)
setting_oidc_username_algo = namespace.add_setting(
    default=DEFAULT_OIDC_USERNAME_ALGO, global_name='OIDC_USERNAME_ALGO',
    help_text=_('Sets the algorithm to create the username.')
)

namespace = SettingNamespace(
    label=_('Authentication OIDC'), name='authentication_oidc'
)

setting_oidc_user_profile_url = namespace.add_setting(
    default=DEFAULT_AUTHENTICATION_OIDC_USER_PROFILE_URL,
    global_name='AUTHENTICATION_OIDC_USER_PROFILE_URL',
    help_text=_('URL for the OIDC user profile page.')
)
