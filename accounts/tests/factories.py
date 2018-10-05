# accounts.tests.factories
# Factory Boy model factories for account models.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Oct 04 19:51:58 2018 -0400
#
# ID: factories.py [] benjamin@bengfort.com $

"""
Factory Boy model factories for account models.
"""

##########################################################################
## Imports
##########################################################################

import factory
import factory.fuzzy

from datetime import date

from accounts.models import CreditScore
from accounts.models import Account, Company
from accounts.models import BalanceSheet, Balance, Transaction


##########################################################################
## Credit and Account Factories
##########################################################################

class CreditScoreFactory(factory.DjangoModelFactory):

    class Meta:
        model = CreditScore

    date = factory.Faker('date_this_decade')
    score = factory.fuzzy.FuzzyInteger(300, 850)
    source = factory.fuzzy.FuzzyChoice([b[0] for b in CreditScore.BUREAUS])
    preferred = True
    memo = factory.Faker('sentence')


class CompanyFactory(factory.DjangoModelFactory):

    class Meta:
        model = Company

    name = "ABC Federal Savings Bank"
    short_name = "ABC"
    url = "https://abc.com/"
    active = True


class ForeignCompanyFactory(CompanyFactory):

    name = "CBA International"
    short_name = "CBA"
    url = "https://cba.co.uk/"


class AccountFactory(factory.DjangoModelFactory):

    class Meta:
        model = Account

    type = Account.CASH
    name = "Everyday Checkings"
    bank = factory.SubFactory(CompanyFactory)
    number = "111222333444"
    active = True
    exclude = False
    order = None
    opened_on = date(2017, 2, 14)
    closed_on = None
    currency = "USD"


class ForeignAccountFactory(AccountFactory):

    name = "Tax Shelter"
    bank = factory.SubFactory(ForeignCompanyFactory)
    currency = "GBP"


class CreditCardFactory(AccountFactory):

    type = Account.CREDIT
    name = "Rewards Mastercard"
    number = factory.Faker('credit_card_number')


class LoanAccountFactory(AccountFactory):

    type = Account.LOAN
    name = "Signature Loan"


class InvestmentAccountFactory(AccountFactory):

    type = Account.INVESTMENT
    name = "Long-Term ETF"


class InsuranceAccountFactory(AccountFactory):

    type = Account.INSURANCE
    name = "Life Insurance"


class BillingAccountFactory(AccountFactory):

    type = Account.BILLING
    name = "Electricity Bill"


##########################################################################
## Balance Sheet Factories
##########################################################################

class BalanceSheetFactory(factory.DjangoModelFactory):

    class Meta:
        model = BalanceSheet


class BalanceFactory(factory.DjangoModelFactory):

    class Meta:
        model = Balance

    sheet = factory.SubFactory(BalanceSheetFactory)


class TransactionFactory(factory.DjangoModelFactory):

    class Meta:
        model = Transaction

    sheet = factory.SubFactory(BalanceSheetFactory)
