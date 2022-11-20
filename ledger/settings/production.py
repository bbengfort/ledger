# ledger.settings.production
# Configuration for the production environment.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 10:38:05 2018 -0400
#
# ID: production.py [36d8a34] benjamin@bengfort.com $

"""
Configuration for the production environment.
"""

##########################################################################
## Imports
##########################################################################

import os
import sentry_sdk

from .base import *  # noqa
from .base import PROJECT, environ_setting

from ..version import get_sentry_release
from sentry_sdk.integrations.django import DjangoIntegration


##########################################################################
## Production Environment
##########################################################################

## Ensure debug mode is not running production
DEBUG = False

## Hosts
ALLOWED_HOSTS = [
    'ledger.bengfort.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://ledger.bengfort.com',
]

## SSL is terminated at Traefik so all requests will be http in the k8s cluster.
SECURE_SSL_REDIRECT = False

## Static files served by WhiteNoise
STATIC_ROOT = os.path.join(PROJECT, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


##########################################################################
## Sentry Error Management
##########################################################################

sentry_sdk.init(
    dsn=environ_setting("SENTRY_DSN"),
    integrations=[DjangoIntegration()],

    # Get release from Heroku environment or specify develop release
    release=get_sentry_release(),
    environment="production",

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,

    # Set a uniform sample rate
    traces_sample_rate=0.5,
)
