import errno
import os

import yaml

from mayan.apps.common.serialization import yaml_load

from .literals import (
    CONFIGURATION_FILENAME, CONFIGURATION_LAST_GOOD_FILENAME
)


class SettingNamespaceSingleton:
    """
    Self hosting bootstrap setting class.
    Allow managing setting in a compatible way before Mayan EDMS starts.
    """
    _setting_kwargs = {}
    _settings = {}

    class SettingNotFound(Exception):
        """Mostly a stand-in or typecast for KeyError for readability."""

    @classmethod
    def load_config_file(cls, filepath):
        try:
            with open(file=filepath) as file_object:
                file_object.seek(0, os.SEEK_END)
                if file_object.tell():
                    file_object.seek(0)
                    try:
                        return yaml_load(stream=file_object)
                    except yaml.YAMLError as exception:
                        exit(
                            'Error loading configuration file: {}; {}'.format(
                                filepath, exception
                            )
                        )
        except IOError as exception:
            if exception.errno == errno.ENOENT:
                # No config file, return empty dictionary
                return {}
            else:
                raise

    @classmethod
    def register_setting(cls, name, klass, kwargs=None):
        cls._settings[name] = klass
        cls._setting_kwargs[name] = kwargs or {}

    def __init__(self, global_symbol_table):
        self.global_symbol_table = global_symbol_table
        self.settings = {}
        for name, klass in self.__class__._settings.items():
            kwargs = self.__class__._setting_kwargs[name].copy()
            kwargs['name'] = name
            setting = klass(**kwargs)
            setting.namespace = self
            self.settings[name] = setting

    def get_config_file_setting(self, name):
        """
        Wrapper for load_config_file to cache the result.
        """
        if hasattr(self, '_cache_file_data'):
            file_data = self._cache_file_data
        else:
            filepath = self.get_setting_value(
                name='CONFIGURATION_FILEPATH'
            )

            file_data = self.load_config_file(filepath=filepath) or {}
            self._cache_file_data = file_data

        try:
            return file_data[name]
        except KeyError:
            raise SettingNamespaceSingleton.SettingNotFound

    def get_setting_value(self, name):
        """
        Wrapper that calls the individual setting .get_value method.
        Convenience method to allow returning setting values from the
        namespace.
        """
        try:
            return self.settings[name].get_value()
        except KeyError:
            raise SettingNamespaceSingleton.SettingNotFound

    def get_values(self, only_critical=False):
        """
        Return a dictionary will all the settings and their respective
        resolved values.
        """
        result = {}
        for name, setting in self.settings.items():
            # If only_critical is set to True load only the settings with
            # the critical flag. Otherwise load all.
            if only_critical and setting.critical or not only_critical:
                try:
                    result[name] = setting.get_value()
                except SettingNamespaceSingleton.SettingNotFound:
                    """
                    Not critical, we just avoid adding it to the result
                    dictionary.
                    """
                except Exception as exception:
                    exit(
                        'Unable to load bootstrap setting; {}'.format(
                            exception
                        )
                    )

        return result

    def update_globals(self, only_critical=False):
        """
        Insert all resolved values into the symbol table of the caller.
        """
        result = self.get_values(only_critical=only_critical)
        self.global_symbol_table.update(result)


class BaseSetting:
    def __init__(
        self, name, critical=False, default_value=None, has_default=False
    ):
        self.critical = critical
        self.name = name
        self.has_default = has_default
        self.default_value = default_value

    def _get_environment_value(self):
        return os.environ.get(
            self.get_environment_name()
        )

    def get_default_value(self):
        return self.default_value

    def get_environment_name(self):
        return 'MAYAN_{}'.format(self.name)

    def get_value(self):
        """
        By default will try to get the value from the namespace symbol table,
        then the configuration file, and finally from the environment.
        """
        # Resolution order
        # 1 - Environment
        # 2 - Config
        # 3 - Global
        # 4 - Default
        try:
            return self.load_environment_value()
        except SettingNamespaceSingleton.SettingNotFound:
            try:
                return self.namespace.get_config_file_setting(name=self.name)
            except SettingNamespaceSingleton.SettingNotFound:
                try:
                    return self.namespace.global_symbol_table[self.name]
                except KeyError:
                    if self.has_default:
                        return self.get_default_value()
                    else:
                        raise SettingNamespaceSingleton.SettingNotFound

    def load_environment_value(self):
        value = self._get_environment_value()

        if value:
            try:
                return yaml_load(stream=value)
            except yaml.YAMLError as exception:
                raise ValueError(
                    'Error loading setting environment variable "{}", '
                    'value: "{}"; {}'.format(
                        self.name, value, exception
                    )
                )
        else:
            raise SettingNamespaceSingleton.SettingNotFound


class FilesystemBootstrapSetting(BaseSetting):
    def __init__(self, name, critical=False, path_parts=None):
        self.critical = critical
        self.has_default = True
        self.name = name
        self.path_parts = path_parts

    def get_default_value(self):
        """
        The default value of this setting class is not static but calculated.
        """
        return os.path.join(
            # Can't use BASE_DIR from django.conf.settings
            # Use it from the global_symbol_table which should be the same
            self.namespace.global_symbol_table.get('BASE_DIR'),
            *self.path_parts
        )

    def get_value(self):
        """
        It is not possible to look for this setting in the config file
        because not even the config file setup has completed.
        This setting only supports being set from the environment.
        """
        try:
            return self.load_environment_value()
        except SettingNamespaceSingleton.SettingNotFound:
            if self.has_default:
                return self.get_default_value()
            else:
                raise SettingNamespaceSingleton.SettingNotFound


class MediaBootstrapSetting(FilesystemBootstrapSetting):
    def get_default_value(self):
        """
        The default value of this setting class is not static but calculated.
        """
        return os.path.join(
            self.namespace.get_setting_value(name='MEDIA_ROOT'),
            *self.path_parts
        )


def smart_yaml_load(value):
    if isinstance(value, dict):
        return value
    else:
        return yaml_load(
            stream=value or '{}'
        )


# FilesystemBootstrapSetting settings

SettingNamespaceSingleton.register_setting(
    klass=MediaBootstrapSetting, kwargs={
        'critical': True, 'path_parts': (CONFIGURATION_FILENAME,)
    }, name='CONFIGURATION_FILEPATH'
)

# MediaBootstrapSetting settings

SettingNamespaceSingleton.register_setting(
    klass=MediaBootstrapSetting, kwargs={
        'critical': True, 'path_parts': (CONFIGURATION_LAST_GOOD_FILENAME,)
    }, name='CONFIGURATION_LAST_GOOD_FILEPATH'
)
SettingNamespaceSingleton.register_setting(
    klass=FilesystemBootstrapSetting, kwargs={
        'critical': True, 'path_parts': ('media',)
    }, name='MEDIA_ROOT'
)

# Normal settings

SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True,
        'default_value': ['127.0.0.1', 'localhost', '[::1]']
    }, name='ALLOWED_HOSTS'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='APPEND_SLASH'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='AUTH_PASSWORD_VALIDATORS'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='AUTHENTICATION_BACKENDS'
)
SettingNamespaceSingleton.register_setting(
    name='DATA_UPLOAD_MAX_MEMORY_SIZE', klass=BaseSetting,
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': None
    }, name='DATABASES'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': False
    }, name='DEBUG'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='DEFAULT_FROM_EMAIL'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='DISALLOWED_USER_AGENTS'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='EMAIL_BACKEND'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='EMAIL_HOST'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='EMAIL_HOST_PASSWORD'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='EMAIL_HOST_USER'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='EMAIL_PORT'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='EMAIL_TIMEOUT'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='EMAIL_USE_SSL'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='EMAIL_USE_TLS'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='FILE_UPLOAD_MAX_MEMORY_SIZE'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': ['127.0.0.1']
    }, name='INTERNAL_IPS'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': 'common:home'
    }, name='LOGIN_REDIRECT_URL'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': 'authentication:login_view'
    }, name='LOGIN_URL'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': 'authentication:login_view'
    }, name='LOGOUT_REDIRECT_URL'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='LANGUAGES'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='LANGUAGE_CODE'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='SESSION_COOKIE_NAME'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='SESSION_ENGINE'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='STATIC_URL'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='STATICFILES_STORAGE'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='TIME_ZONE'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='WSGI_APPLICATION'
)

# Celery

SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': True
    }, name='CELERY_TASK_ALWAYS_EAGER'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='CELERY_BROKER_LOGIN_METHOD'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': 'memory://'
    }, name='CELERY_BROKER_URL'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='CELERY_BROKER_USE_SSL'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, name='CELERY_RESULT_BACKEND'
)

# Mayan

SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': False
    }, name='COMMON_DISABLE_LOCAL_STORAGE'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'critical': True, 'has_default': True, 'default_value': ()
    }, name='COMMON_DISABLED_APPS'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'critical': True, 'has_default': True, 'default_value': ()
    }, name='COMMON_EXTRA_APPS'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'critical': True, 'has_default': True, 'default_value': ()
    }, name='COMMON_EXTRA_APPS_PRE'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': None
    }, name='DATABASE_ENGINE'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': None
    }, name='DATABASE_NAME'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': None
    }, name='DATABASE_USER'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': None
    }, name='DATABASE_PASSWORD'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': None
    }, name='DATABASE_HOST'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': None
    }, name='DATABASE_PORT'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': 0
    }, name='DATABASE_CONN_MAX_AGE'
)
SettingNamespaceSingleton.register_setting(
    klass=BaseSetting, kwargs={
        'has_default': True, 'default_value': False
    }, name='TESTING'
)
