# accounts.apps
# Accounts app congfiguration
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed May 02 15:41:02 2018 -0400
#
# ID: apps.py [0395481] benjamin@bengfort.com $

"""
Account app congfiguration
"""

##########################################################################
## Imports
##########################################################################

from django.apps import AppConfig


##########################################################################
## AppConfig
##########################################################################

class AccountsConfig(AppConfig):

    name = 'accounts'
    verbose_name = 'accounting'

    def ready(self):
        import accounts.signals # noqa
