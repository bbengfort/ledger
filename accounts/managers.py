# accounts.managers
# Query managers for the accounts models.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Fri May 04 11:04:45 2018 -0400
#
# ID: managers.py [] benjamin@bengfort.com $

"""
Query managers for the accounts models.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models


##########################################################################
## Account Type Managers
##########################################################################

class AccountTypeManager(models.Manager):

    def __init__(self, account_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_type = account_type

    def get_queryset(self):
        return super().get_queryset().filter(type=self.account_type)


class AccountBalanceTypeManager(models.Manager):

    # Copied here to prevent recursive imports
    CASH = "Ca"
    CREDIT = "Cc"
    LOAN = "Ln"
    INVESTMENT = "Iv"
    INSURANCE = "Is"
    BILLING = "Bl"

    def cash_accounts(self):
        return self.filter(account__type=self.CASH)

    def credit_accounts(self):
        return self.filter(account__type=self.CREDIT)

    def loan_accounts(self):
        return self.filter(account__type=self.LOAN)
        
    def investment_accounts(self):
        return self.filter(account__type=self.INVESTMENT)

    def insurance_accounts(self):
        return self.filter(account__type=self.INSURANCE)

    def billing_accounts(self):
        return self.filter(account__type=self.BILLING)
