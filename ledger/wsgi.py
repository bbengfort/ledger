# ledger.wsgi
# WSGI config for ledger project.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 10:20:58 2018 -0400
#
# ID: wsgi.py [36d8a34] benjamin@bengfort.com $

"""
WSGI config for ledger project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

##########################################################################
## Imports
##########################################################################

import os
import dotenv

from django.core.wsgi import get_wsgi_application

##########################################################################
## WSGI Configuration
##########################################################################

# load .env file
dotenv.load_dotenv(dotenv.find_dotenv())

# set default environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ledger.settings.development")

# export the wsgi application for import
application = get_wsgi_application()
