# accounts.models.balance
# Balance sheet related models.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed May 02 15:41:23 2018 -0400
#
# ID: balance.py [] benjamin@bengfort.com $

"""
Balance sheet related models.
"""

##########################################################################
## Imports
##########################################################################

from datetime import date
from decimal import Decimal

from django.db import models
from django.urls import reverse

from ..managers import BalanceSheetManager
from ..managers import AccountBalanceTypeManager


##########################################################################
## Balance Sheet
##########################################################################

class BalanceSheet(models.Model):
    """
    A monthly record of account balances and transactions. Generally speaking
    there is only one balance sheet per month (somewhat enforced by the unique
    for month field on the title of the balance sheet), and the balance sheet
    for the month is created when the user moves forward in time to that month.
    """

    date = models.DateField(
        null=False, blank=False, default=date.today,
        help_text="Date of accounting"
    )
    title = models.CharField(
        max_length=255, null=False, blank=True, unique_for_month="date",
        help_text="A short title describing the balance sheet",
    )
    accounts = models.ManyToManyField(
        'accounts.Account', through='accounts.Balance', related_name='+',
        help_text="Accounts modified by the balance sheet",
    )
    memo = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="A short memo or note describing the balance sheet",
    )

    class Meta:
        db_table = "balance_sheets"
        ordering = ("-date",)
        get_latest_by = "date"

    # Balance sheet manager
    objects = BalanceSheetManager()

    def get_absolute_url(self):
        date = self.date.strftime("%Y %m").split()
        kwargs = dict(zip(('year', 'month'), date))

        return reverse('sheets-detail', kwargs=kwargs)

    def get_api_url(self):
        date = self.date.strftime("%Y-%m-%d")
        return reverse('api:sheets-detail', kwargs={'date': date})

    def is_active(self):
        """
        Returns True if the date of the balance sheet is within 15 days of
        the current date (either before or after). The idea here is that the
        balance sheet date is probably on the 1st-4th of the month, so this
        balance sheet is active if we're in the last two weeks of the previous
        month, or the first two weeks of the next month.

        The possibility exists for two balance sheets to be active.
        """
        days = abs((date.today() - self.date).days)
        return days < 15

    def __str__(self):
        return self.title


##########################################################################
##  Account Balances
##########################################################################

class Balance(models.Model):
    """
    A Balance represents the state of an account for a particular moment in
    time, specified by the associated balance sheet (usually once per month).
    Balances are modified by transactions which either credit the account
    (e.g. add money to the account) or debit the account (remove money from
    the account).
    """

    sheet = models.ForeignKey(
        'accounts.BalanceSheet', on_delete=models.CASCADE, null=False,
        related_name='balances',
        help_text="The balance sheet for the associated balance",
    )
    account = models.ForeignKey(
        'accounts.Account', on_delete=models.CASCADE, null=False,
        related_name='balances', limit_choices_to={'active': True},
        help_text="The account associated with the balance"
    )
    beginning = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, null=False, default=0.0,
        help_text="Beginning balance of the account"
    )
    ending = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=0.0,
        help_text="Ending balance after transactions"
    )

    class Meta:
        db_table = "balances"
        ordering = ("-sheet__date", "account__order")
        unique_together = ('sheet', 'account')

    # Account type managers
    objects = AccountBalanceTypeManager()

    @property
    def date(self):
        return self.sheet.date

    def get_api_url(self):
        kwargs = {
            "pk": self.pk,
            "sheets_date": self.date.strftime("%Y-%m-%d"),
        }
        return reverse("sheets-api:sheets-balances-detail", kwargs=kwargs)

    def credits(self):
        """
        Returns all associated credits to this account for the given balance
        sheet (returns an empty list if there are no credits).
        """
        return self.sheet.transactions.filter(credit=self.account)

    def debits(self):
        """
        Returns all associated debits to this account for the given balance
        sheet (returns an empty list if there are no debits).
        """
        return self.sheet.transactions.filter(debit=self.account)

    def update_ending_balance(self):
        """
        (Re)computes the ending balance based on all associated transactions.
        Note, that this method does not save the ending balance, just sets it.
        """
        total = self.beginning
        total += self.credit_amount(completed=False)  # will be negative
        total += self.debit_amount(completed=False)   # will be positive
        self.ending = total

    def credit_amount(self, completed=False):
        # NOTE: must return negative value
        query = self.credits().filter(complete=completed)
        return -1 * self._total_amount(query)

    def debit_amount(self, completed=False):
        # NOTE: must return positive value
        query = self.debits().filter(complete=completed)
        return self._total_amount(query)

    def _total_amount(self, query):
        """
        Sums the amount for the given query and returns a Decimal value for
        the total. CANNOT return either None or float types!
        """
        query = query.values("amount").aggregate(total=models.Sum("amount"))
        return query["total"] or Decimal(0.0)

    def __str__(self):
        if self.ending == 0:
            return "{} beginning with ${:,} on {}".format(
                self.account, self.beginning, self.date.strftime("%Y-%m-%d")
            )

        return "{} ending with ${:,} on {}".format(
            self.account, self.ending, self.date.strftime("%Y-%m-%d")
        )


##########################################################################
## Transactions
##########################################################################

class Transaction(models.Model):
    """
    Represents a transfer of funds from the debiting account to the credited
    account. This transfer can be to pay a bill, e.g. from a cash or credit
    account to a billing account, or between accounts.

    Note: A debit is an accounting entry that either increases an asset or
    expense account, or decreases a liability or equity account. It is
    positioned to the left in an accounting entry. A credit is an accounting
    entry that either increases a liability or equity account, or decreases an
    asset or expense account.

    Generally speaking, the source for spending money in a transaction in the
    account is credit (that is, an entry is made on the right side of the
    account's ledger), and what the money obtained with the credit is
    described as a debit (that is, an entry is made on the left side)
    """

    sheet = models.ForeignKey(
        'accounts.BalanceSheet', on_delete=models.CASCADE, null=False,
        related_name='transactions',
        help_text="The balance sheet for the associated transaction",
    )
    date = models.DateField(
        null=False, blank=False, default=date.today,
        help_text="The date of the transaction"
    )
    credit = models.ForeignKey(
        'accounts.Account', on_delete=models.CASCADE, null=False,
        related_name="credits", limit_choices_to={'active': True},
        help_text="The source of funds for the transaction"
    )
    debit = models.ForeignKey(
        'accounts.Account', on_delete=models.CASCADE, null=False,
        related_name="debits", limit_choices_to={'active': True},
        help_text="The destination of funds for the transaction"
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, null=False, default=0.0,
        help_text="The amount of the transaction"
    )
    complete = models.BooleanField(
        default=False,
        help_text="If the transaction is included in the beginning balance"
    )
    memo = models.CharField(
        max_length=500, blank=True, null=True,
        help_text="A short memo or note describing the transaction",
    )

    class Meta:
        db_table = "transactions"
        ordering = ("-date",)
        get_latest_by = "date"

    def __str__(self):
        return "Transfer ${:,} from {} to {} on {}".format(
            self.amount, self.credit, self.debit, self.date
        )
