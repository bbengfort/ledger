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
from .base import *


##########################################################################
## Development Environment
##########################################################################

ALLOWED_HOSTS = ('127.0.0.1', 'localhost')

MEDIA_ROOT = os.path.join(PROJECT, 'media')
STATIC_ROOT = 'staticfiles'
