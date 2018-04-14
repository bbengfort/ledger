#!/usr/bin/env python
# manage.py
# Django management script
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 10:34:10 2018 -0400
#
# ID: manage.py [] benjamin@bengfort.com $

"""
Django management script
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import dotenv

try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc


##########################################################################
## Main Method
##########################################################################

if __name__ == "__main__":
    # load .env file
    dotenv.load_dotenv(dotenv.find_dotenv())

    # set default environment variables
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ledger.settings.development")

    # execute the django admin script
    execute_from_command_line(sys.argv)
