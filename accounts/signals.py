# accounts.signals
# Signals used by accounts models - imported by the apps.py configuration.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu May 03 11:13:30 2018 -0400
#
# ID: signals.py [] benjamin@bengfort.com $

"""
Signals used by accounts models - imported by the apps.py configuration.
"""

##########################################################################
## Imports
##########################################################################

from .models import BalanceSheet

from django.dispatch import receiver
from django.db.models.signals import pre_save


@receiver(pre_save, sender=BalanceSheet, dispatch_uid="balance_sheet_unique_for_month_title")
def update_balance_sheet_title(sender, instance, *args, **kwargs):
    """
    Creates the balance sheet title, which is unique for month with the
    associated date, so has the effect of ensuring one balance sheet per month
    unless the user creates a custom title.
    """
    if not instance.title:
        instance.title = "Bills and Banking for {}".format(
            instance.date.strftime("%b %d, %Y")
        )
