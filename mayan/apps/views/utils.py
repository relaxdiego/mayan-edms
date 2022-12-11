import logging

from django.urls import resolve as django_resolve
from django.urls.base import get_script_prefix

logger = logging.getLogger(name=__name__)


def convert_to_id_list(items):
    return ','.join(
        map(str, items)
    )


def resolve(path, urlconf=None):
    path = '/{}'.format(
        path.replace(
            get_script_prefix(), '', 1
        )
    )
    return django_resolve(path=path, urlconf=urlconf)
