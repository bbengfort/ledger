# ledger.settings.container
# Configuration for container operations.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sun Nov 20 08:21:47 2022 -0600
#
# ID: container.py [] benjamin@bengfort.com $

"""
Configuration for container operations.
"""

##########################################################################
## Imports
##########################################################################

import os

from .base import *  # noqa
from .base import PROJECT


##########################################################################
## Container Environment
##########################################################################

## Ensure debug mode is not running production
DEBUG = False

## Hosts
ALLOWED_HOSTS = [
    'ledger.bengfort.com',
]

## Static files served by WhiteNoise
STATIC_ROOT = os.path.join(PROJECT, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
