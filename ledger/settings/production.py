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
from .base import *  # noqa
from .base import PROJECT


##########################################################################
## Production Environment
##########################################################################

## Ensure debug mode is not running production
DEBUG = False

## Hosts
ALLOWED_HOSTS = [
    'bengfort-ledger.herokuapp.com',
    'ledger.bengfort.com',
]

## Use SSL
SECURE_SSL_REDIRECT = True

## Static files served by WhiteNoise
STATIC_ROOT = os.path.join(PROJECT, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
