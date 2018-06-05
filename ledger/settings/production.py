# ledger.settings.production
# Configuration for the production environment.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 10:38:05 2018 -0400
#
# ID: production.py [] benjamin@bengfort.com $

"""
Configuration for the production environment.
"""

##########################################################################
## Imports
##########################################################################

import os
from .base import *


##########################################################################
## Production Environment
##########################################################################

## Hosts
ALLOWED_HOSTS    = [
    'bengfort-ledger.herokuapp.com',
    'ledger.bengfort.com',
]

## Use SSL
SECURE_SSL_REDIRECT = True 

## Static files served by WhiteNoise
STATIC_ROOT = os.path.join(PROJECT, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
