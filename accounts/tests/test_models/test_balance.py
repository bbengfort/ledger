# accounts.tests.test_models.test_balance
# Tests for the Balance Sheet and related models.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Nov 01 10:36:11 2018 -0400
#
# ID: test_balance.py [] benjamin@bengfort.com $

"""
Tests for the Balance Sheet and related models.
"""

##########################################################################
## Imports
##########################################################################

import re
import pytest

from ..factories import *
from decimal import Decimal

# All tests in this module use the database
pytestmark = pytest.mark.django_db


##########################################################################
## Balance Sheet Tests
##########################################################################

SHEET_TITLE = re.compile(r'Bills and Banking for (\w+) (\d+), (\d+)')

def test_balance_sheet_title():
    """
    Balance Sheets should generate a title based on date.
    """

    b = BalanceSheet(date=this_month())
    assert b.title == ""
    b.save()
    assert b.title != ""
    assert SHEET_TITLE.match(b.title)


@pytest.mark.skip(reason="requires freezegun to test accurately")
def test_balance_sheet_active():
    """
    Ensure this month's balance sheet is marked as active.
    """
    pass


def test_balance_ending():
    """
    Ensure a beginning balance without transactions matches ending balance
    """

    b = BalanceFactory()
    assert b.credits().count() == 0
    assert b.debits().count() == 0
    assert b.beginning == b.ending


def test_balance_sheet_scenario():
    """
    Test a simple balance sheet scenario with 2 cash accounts, 2 credit cards,
    and several billing accounts, correctly updated as transactions and
    balances are added.
    """

    # Create the balance sheet for the month
    # TODO: make this a fixture for reuse elsewhere
    sheet = BalanceSheetFactory()
    assert sheet.accounts.count() == 0

    # Create the various accounts
    checking = AccountFactory()
    savings  = AccountFactory(name="Performance Savings", number="111222333455")
    mastercard = CreditCardFactory()
    visa = CreditCardFactory(name="Mileage Visa")

    # Add the initial balances
    checking_balance = BalanceFactory(sheet=sheet, account=checking, beginning=Decimal("5321.56"))
    savings_balance = BalanceFactory(sheet=sheet, account=savings, beginning=Decimal("46322.21"))
    mastercard_balance = BalanceFactory(sheet=sheet, account=mastercard, beginning=Decimal("-1822.49"))
    visa_balance = BalanceFactory(sheet=sheet, account=visa, beginning=Decimal("-4873.11"))

    # Check the current balance sheet
    assert sheet.accounts.count() == 4
    assert sheet.balances.count() == 4
    assert sheet.balances.cash_accounts().count() == 2
    assert sheet.balances.credit_accounts().count() == 2
    assert sheet.transactions.count() == 0

    for balance in sheet.balances.all():
        assert balance.beginning == balance.ending

    # Create the various transactions for bill paying and balancing the checkbook
    TransactionFactory.create(sheet=sheet, date=this_month(3), credit=checking, amount=Decimal("192.22"), debit=BillingAccountFactory(name="Electricity Bill"))
    TransactionFactory.create(sheet=sheet, date=this_month(4), credit=checking, amount=Decimal("68.97"), debit=BillingAccountFactory(name="Water Meter"))
    TransactionFactory.create(sheet=sheet, date=this_month(5), credit=visa, amount=Decimal("208.69"), debit=BillingAccountFactory(name="Cable Internet"))
    TransactionFactory.create(sheet=sheet, date=this_month(14), credit=visa, amount=Decimal("112.54"), debit=BillingAccountFactory(name="Mobile Phone"))
    TransactionFactory.create(sheet=sheet, date=this_month(12), credit=mastercard, amount=Decimal("14.99"), debit=BillingAccountFactory(name="Netflix"))
    TransactionFactory.create(sheet=sheet, date=this_month(21), credit=mastercard, amount=Decimal("38.75"), debit=BillingAccountFactory(name="Newspaper Subscription"))
    TransactionFactory.create(sheet=sheet, date=this_month(5), credit=visa, amount=Decimal("75.11"), debit=BillingAccountFactory(name="Trash Collection"))
    TransactionFactory.create(sheet=sheet, date=this_month(1), credit=visa, amount=Decimal("385.45"), debit=BillingAccountFactory(name="Donations"))
    TransactionFactory.create(sheet=sheet, date=this_month(1), credit=checking, debit=visa, amount=Decimal("3712.65"))
    TransactionFactory.create(sheet=sheet, date=this_month(1), credit=checking, debit=mastercard, amount=Decimal("1598.33"))
    TransactionFactory.create(sheet=sheet, date=this_month(1), credit=savings, debit=checking, amount=Decimal("750.61"))

    # Check the balances have been correctly recomputed
    checking_balance.refresh_from_db()
    assert checking_balance.beginning == Decimal("5321.56")
    assert checking_balance.ending == Decimal("500.00")
    assert checking_balance.credits().count() == 4
    assert checking_balance.debits().count() == 1
    assert checking_balance.credit_amount() == Decimal("-5572.17")
    assert checking_balance.debit_amount() == Decimal("750.61")

    savings_balance.refresh_from_db()
    assert savings_balance.beginning == Decimal("46322.21")
    assert savings_balance.ending == Decimal("45571.60")
    assert savings_balance.credits().count() == 1
    assert savings_balance.debits().count() == 0
    assert savings_balance.credit_amount() == Decimal("-750.61")
    assert savings_balance.debit_amount() == Decimal("0.00")

    mastercard_balance.refresh_from_db()
    assert mastercard_balance.beginning == Decimal("-1822.49")
    assert mastercard_balance.ending == Decimal("-277.90")
    assert mastercard_balance.credits().count() == 2
    assert mastercard_balance.debits().count() == 1
    assert mastercard_balance.credit_amount() == Decimal("-53.74")
    assert mastercard_balance.debit_amount() == Decimal("1598.33")

    visa_balance.refresh_from_db()
    assert visa_balance.beginning == Decimal("-4873.11")
    assert visa_balance.ending == Decimal("-1942.25")
    assert visa_balance.credits().count() == 4
    assert visa_balance.debits().count() == 1
    assert visa_balance.credit_amount() == Decimal("-781.79")
    assert visa_balance.debit_amount() == Decimal("3712.65")

    # Check the balance sheet totals
    sheet.transactions.count() == 11
    assert sheet.accounts.count() == 4
    assert sheet.balances.count() == 4
    assert sheet.balances.cash_accounts().count() == 2
    assert sheet.balances.credit_accounts().count() == 2
