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

from .models import Balance
from .models import Transaction
from .models import BalanceSheet

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save


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


@receiver(post_save, sender=Transaction, dispatch_uid="update_ending_balance_after_transaction")
def update_balance_after_transaction(sender, instance, *args, **kwargs):
    """
    Recomputes the ending balance for the accounts credited and debited on the
    transaction, saving their new values back to disk.
    """
    for account in (instance.credit, instance.debit):
        try:
            balance = instance.sheet.balances.get(account=account)
            balance.update_ending_balance()
            balance.save()
        except Balance.DoesNotExist:
            continue


@receiver(pre_save, sender=Balance, dispatch_uid="update_ending_balance_on_save")
def update_ending_balance(sender, instance, *args, **kwargs):
    """
    Updates the ending balance when the Balance is saved.
    """
    instance.update_ending_balance()


@receiver(post_save, sender=BalanceSheet, dispatch_uid="update_all_ending_balances_on_sheet")
def update_all_ending_balances(sender, instance, *args, **kwargs):
    """
    Updates all ending balances when the sheet is saved.
    """
    #TODO: Remove this signal in favor of a manual method
    for balance in instance.balances.all():
        balance.update_ending_balance()
        balance.save()
