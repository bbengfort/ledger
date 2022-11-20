# ledger.settings.testing
# Testing settings to enable testing on Travis with Django tests.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Apr 14 11:02:40 2018 -0400
#
# ID: testing.py [36d8a34] benjamin@bengfort.com $

"""
Testing settings to enable testing on Travis with Django tests.
"""

##########################################################################
## Imports
##########################################################################

import dj_database_url

from .base import *  # noqa
from .base import REST_FRAMEWORK


##########################################################################
## Test Settings
##########################################################################

## Hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000', 'http://127.0.0.1:8000',
]

## Database Settings
## https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600),
}

DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['default']['TEST'] = {'NAME': 'ledger_test'}


STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

## Content without side effects
MEDIA_ROOT = "/tmp/ledger_test/media"
STATIC_ROOT = "/tmp/ledger_test/static"

##########################################################################
## Django REST Framework
##########################################################################

REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = (
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
)
