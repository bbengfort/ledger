# ledger.settings.development
# Configuration for the development environment.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 10:38:05 2018 -0400
#
# ID: development.py [36d8a34] benjamin@bengfort.com $

"""
Configuration for the development environment.
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
## Development Environment
##########################################################################

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000', 'http://127.0.0.1:8000',
]

MEDIA_ROOT = os.path.join(PROJECT, "tmp", "media")

## Static files served by WhiteNoise nostatic server
STATIC_ROOT = os.path.join(PROJECT, "tmp", "static")
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Debugging email without SMTP
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(PROJECT, "tmp", "outbox")


##########################################################################
## Sentry Error Management
##########################################################################

sentry_sdk.init(
    dsn=environ_setting("SENTRY_DSN"),
    integrations=[DjangoIntegration()],

    # Get release from Heroku environment or specify develop release
    release=get_sentry_release(),
    environment="development",

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,

    # Set a uniform sample rate
    traces_sample_rate=1.0,
)
