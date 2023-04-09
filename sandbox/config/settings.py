from .settings_original import *


INSTALLED_APPS += ['django_htmx', 'htmx_viewsets', 'test_db', "debug_toolbar", 'django_extensions']

MIDDLEWARE += ['django_htmx.middleware.HtmxMiddleware', "debug_toolbar.middleware.DebugToolbarMiddleware",]
INTERNAL_IPS = ["127.0.0.1",]

_DB = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'htmx_viewsets',
    'USER': 'fh',
    'PASSWORD': 'skhgmVI678',
    'HOST': 'localhost',
    'PORT': 5432,
    }

DATABASES = {'default': _DB}
