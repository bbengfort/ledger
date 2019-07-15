# account.tests.conftest
# pytest fixtures and configuration for account tests
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Jul 14 09:55:57 2019 -0400
#
# Copyright (C) 2019 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: conftest.py [] benjamin@bengfort.com $

"""
pytest fixtures and configuration for account tests
"""

##########################################################################
## Imports
##########################################################################

import pytest

from decimal import Decimal

from .factories import this_month
from .factories import AccountFactory, CreditCardFactory, BillingAccountFactory
from .factories import BalanceSheetFactory, BalanceFactory, TransactionFactory


@pytest.fixture()
def balance_sheet(db):
    sheet = BalanceSheetFactory.create()

    # Create the various accounts
    checking = AccountFactory()
    savings = AccountFactory(name="Performance Savings", number="111222333455")
    mastercard = CreditCardFactory()
    visa = CreditCardFactory(name="Mileage Visa")

    # Add the initial balances
    BalanceFactory(sheet=sheet, account=checking, beginning=Decimal("5321.56"))
    BalanceFactory(sheet=sheet, account=savings, beginning=Decimal("46322.21"))
    BalanceFactory(sheet=sheet, account=mastercard, beginning=Decimal("-1822.49"))
    BalanceFactory(sheet=sheet, account=visa, beginning=Decimal("-4873.11"))

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

    return sheet
