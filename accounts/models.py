# accounts.models
# Accounts models and base models.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed May 02 15:41:23 2018 -0400
#
# ID: models.py [0395481] benjamin@bengfort.com $

"""
Accounts models and base models.
"""

##########################################################################
## Imports
##########################################################################

from datetime import date

from django.db import models
from django.urls import reverse

from .utils import Currency
from .managers import AccountTypeManager, AccountBalanceTypeManager


##########################################################################
## Financial Account
##########################################################################

class Account(models.Model):
    """
    Represents a financial account held by a bank of various types, including
    cash accounts, investment accounts, credit accounts, and loans.

    I chose to store all accounts in a single table rather than as individual
    tables since there are relatively few account rows. Additional information
    for account types that require it may be created in different apps, but
    for now, this is the simplest way to organize the ledger.
    """

    # Acount Type Definitions
    CASH = "Ca"
    CREDIT = "Cc"
    LOAN = "Ln"
    INVESTMENT = "Iv"
    INSURANCE = "Is"
    BILLING = "Bl"

    ACCOUNT_TYPES = (
        (CASH, "Cash"),
        (CREDIT, "Credit Card"),
        (LOAN, "Loan"),
        (INVESTMENT, "Investment"),
        (INSURANCE, "Insurance"),
        (BILLING, "Billing"),
    )

    # Account Fields
    type = models.CharField(
        max_length=2, choices=ACCOUNT_TYPES, default=CASH,
        help_text="The account type for related accounts"
    )
    name = models.CharField(
        max_length=255, null=False, blank=False,
        help_text="Nickname, must be unique to the bank"
    )
    bank = models.ForeignKey(
        'accounts.Company', on_delete=models.CASCADE, null=False,
        related_name='accounts', limit_choices_to={'active': True},
        help_text="Associated financial institution"
    )
    number = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Account number assigned by the bank"
    )
    active = models.BooleanField(
        default=True,
        help_text="Display account in primary accounts list"
    )
    exclude = models.BooleanField(
        default=False,
        help_text="Exclude account from overview and aggregations"
    )
    order = models.PositiveSmallIntegerField(
        default=None, null=True, blank=True,
        help_text="User defined order for display"
    )
    opened_on = models.DateField(
        null=True, blank=True,
        help_text="Date the account was opened"
    )
    closed_on = models.DateField(
        null=True, blank=True,
        help_text="Date the account was closed on"
    )
    currency = models.CharField(
        max_length=3, null=False, blank=False, default=Currency.USD.value,
        choices=Currency.choices(),
        help_text="Specify the currency associated with the account",
    )

    class Meta:
        db_table = "accounts"
        ordering = ("bank__short_name", "name",)
        unique_together = ('name', 'bank')

    # Account type managers
    objects = models.Manager()
    cash_accounts = AccountTypeManager(CASH)
    credit_accounts = AccountTypeManager(CREDIT)
    loan_accounts = AccountTypeManager(LOAN)
    investment_accounts = AccountTypeManager(INVESTMENT)
    insurance_accounts = AccountTypeManager(INSURANCE)
    billing_accounts = AccountTypeManager(BILLING)

    @property
    def is_liability(self):
        """
        Returns True if the account type is a liability - e.g. an obligation
        to pay another entity. This includes credit cards, loans, and bills.
        """
        return self.type in {
            self.CREDIT, self.LOAN, self.BILLING
        }

    @property
    def is_asset(self):
        """
        Returns true if the account type is an asset or expense account. E.g.
        a cash account (checking or saving) or an investment.
        """
        return self.type in {
            self.CASH, self.INVESTMENT
        }

    def __str__(self):
        return "{} {}".format(self.bank.short_name, self.name)


##########################################################################
## Financial Institution
##########################################################################

class Company(models.Model):
    """
    A simple representation of a financial institution. A company is
    associated with one or more accounts, though generally no more than one
    or two.

    I've opted to call this table Company instead of Bank because this simply
    refers to the corporate organization where money can be transferred from
    or to -- including billing accounts. For example, Verizon is an example
    of a record that may be stored here, since it includes TV and Cell Phone
    accounts that need to be stored in this table.
    """

    name = models.CharField(
        max_length=255, null=False, blank=False, unique=True,
        help_text="Name of the financial institution"
    )
    short_name = models.CharField(
        max_length=32, null=True, blank=True,
        help_text="Short name for display purposes"
    )
    url = models.URLField(
        max_length=255, null=True, blank=True,
        help_text="URL of the bank for quick access"
    )
    active = models.BooleanField(
        default=True,
        help_text="Display bank in primary banks list"
    )

    class Meta:
        db_table = "companies"
        ordering = ("short_name",)
        verbose_name_plural = "companies"

    def __str__(self):
        return self.short_name


##########################################################################
## Balance Sheets and Transactions
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
        help_text="A short memo or note describing the transaction",
    )

    class Meta:
        db_table = "balance_sheets"
        ordering = ("-date",)
        get_latest_by = "date"

    def get_absolute_url(self):
        date = self.date.strftime("%Y %m %d").split()
        kwargs = dict(zip(('year', 'month', 'day'), date))

        return reverse('sheets-detail', kwargs=kwargs)

    def __str__(self):
        return self.title


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

        for transaction in self.credits():
            # Deduct amount from transactions where this account is credited
            if not transaction.complete:
                total -= transaction.amount

        for transaction in self.debits():
            # Add amount from transactions where this account is debited
            if not transaction.complete:
                total += transaction.amount

        self.ending = total

    def __str__(self):
        if self.ending == 0:
            return "{} beginning with ${:,} on {}".format(
                self.account, self.beginning, self.date.strftime("%Y-%m-%d")
            )

        return "{} ending with ${:,} on {}".format(
            self.account, self.ending, self.date.strftime("%Y-%m-%d")
        )


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
