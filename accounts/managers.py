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
from django.conf import settings

from datetime import date, datetime
from dateutil.relativedelta import relativedelta


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
    CHARITABLE = "Dn"

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

    def charitable_accounts(self):
        return self.filter(account__type=self.CHARITABLE)

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

    def charitable_accounts(self):
        return self.get_queryset().charitable_accounts()


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

    def get_date(self, day):
        """
        Returns the balance sheet from the specified date string as YYYY-MM
        """
        day = datetime.strptime(day, "%Y-%m")
        return self.get_month(day.year, day.month)


class BalanceSheetManager(models.Manager):

    def get_queryset(self):
        return BalanceSheetQuerySet(self.model, using=self._db)

    def get_month(self, year, month):
        # Pass-through to the queryset method
        return self.get_queryset().get_month(year, month)

    def get_date(self, day):
        # Pass-through to the queryset method
        return self.get_queryset().get_date(day)

    def get_current(self, raise_on_error=True):
        """
        Returns the current balance sheet for the current month if today is
        before the 10th of the month, otherwise it returns the balance sheet
        for next month (e.g. the balance sheet currently being worked on).

        If the balance sheet doesn't exist or there are multiple balance sheets
        for the specified month, an exception is raised.
        """
        today = date.today()

        # TODO: change the day of month to be a setting
        if today.day <= settings.BILLING_DAY_OF_MONTH:
            month = today
        else:
            month = (today + relativedelta(months=1)).replace(day=1)

        try:
            return self.get_month(month.year, month.month)
        except Exception:
            if raise_on_error:
                raise
            return None


##########################################################################
## Transactions Manager
##########################################################################

class TransactionQuerySet(models.QuerySet):

    def total(self):
        """
        Compute the total amount of the transactions
        """
        return self.aggregate(Sum("amount"))

    def expenses(self):
        """
        Filter transactions that are not transfers.
        """
        return self.exclude(debit__type__in=['Ca', 'Iv'])

    def transfers(self):
        """
        Filter transactions that are to cash or investment accounts.
        """
        return self.filter(debit__type__in=['Ca', 'Iv'])


class TransactionManager(models.Manager):

    def get_queryset(self):
        return TransactionQuerySet(self.model, using=self._db)

    def total(self):
        return self.get_queryset().total()

    def expenses(self):
        return self.get_queryset().expenses()

    def transfers(self):
        return self.get_queryset().transfers()
