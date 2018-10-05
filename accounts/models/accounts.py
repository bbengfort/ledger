# accounts.models.accounts
# Accounts and baking related models.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed May 02 15:41:23 2018 -0400
#
# ID: accounts.py [] benjamin@bengfort.com $

"""
Accounts and baking related models.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models

from ..utils import Currency
from ..managers import AccountTypeManager


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
            self.CREDIT, self.LOAN, self.BILLING,
        }

    @property
    def is_asset(self):
        """
        Returns true if the account type is an asset or expense account. E.g.
        a cash account (checking or saving) or an investment.
        """
        return self.type in {
            self.CASH, self.INVESTMENT, self.INSURANCE,
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
