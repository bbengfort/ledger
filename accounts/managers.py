# accounts.managers
# Query managers for the accounts models.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Fri May 04 11:04:45 2018 -0400
#
# ID: managers.py [164f0d2] benjamin@bengfort.com $

"""
Query managers for the accounts models.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models
from django.db.models import Sum

from datetime import datetime


##########################################################################
## Querysets
##########################################################################

class BalanceQuerySet(models.QuerySet):

    # Copied here to prevent recursive imports
    CASH = "Ca"
    CREDIT = "Cc"
    LOAN = "Ln"
    INVESTMENT = "Iv"
    INSURANCE = "Is"
    BILLING = "Bl"

    def active(self):
        return self.filter(account__active=True)

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

    def totals(self):
        return self.filter(
            account__active=True, account__exclude=False
        ).aggregate(
            Sum("beginning"), Sum("ending")
        )


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

    def get_queryset(self):
        return BalanceQuerySet(self.model, using=self._db)

    def cash_accounts(self):
        return self.get_queryset().cash_accounts()

    def credit_accounts(self):
        return self.get_queryset().credit_accounts()

    def loan_accounts(self):
        return self.get_queryset().loan_accounts()

    def investment_accounts(self):
        return self.get_queryset().investment_accounts()

    def insurance_accounts(self):
        return self.get_queryset().insurance_accounts()

    def billing_accounts(self):
        return self.get_queryset().billing_accounts()


##########################################################################
## Balance Sheet Manager
##########################################################################

class BalanceSheetQuerySet(models.QuerySet):

    def get_month(self, year, month):
        """
        Returns the balance sheet for the specified year and month (ints). This
        method raises a DoesNotExist error if no balance sheet for the year and
        month combo exists and raises a MultipleObjectsReturned error if there
        are multiple balance sheet objects for the specified year and month.
        """
        queryset = self.filter(date__year=year).filter(date__month=month)
        return queryset.get()

    def get_date(self, date):
        """
        Returns the balance sheet from the specified date string as YYYY-MM
        """
        date = datetime.strptime(date, "%Y-%m")
        return self.get_month(date.year, date.month)


class BalanceSheetManager(models.Manager):

    def get_queryset(self):
        return BalanceSheetQuerySet(self.model, using=self._db)
