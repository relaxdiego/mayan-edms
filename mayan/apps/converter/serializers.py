from django.utils.translation import ugettext_lazy as _

from mayan.apps.rest_api import serializers

from .models import Asset


class AssetSerializer(serializers.HyperlinkedModelSerializer):
    image_url = serializers.HyperlinkedIdentityField(
        label=_('Image URL'), lookup_url_kwarg='asset_id',
        view_name='rest_api:asset-image'
    )

    class Meta:
        extra_kwargs = {
            'url': {
                'label': _('URL'),
                'lookup_url_kwarg': 'asset_id',
                'view_name': 'rest_api:asset-detail'
            }
        }
        fields = (
            'file', 'label', 'id', 'image_url', 'internal_name', 'url'
        )
        model = Asset
