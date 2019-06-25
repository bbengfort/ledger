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

import random
import factory
import factory.fuzzy

from datetime import date, timedelta

from accounts.models import Payment
from accounts.models import CreditScore
from accounts.models import Account, Company
from accounts.models import BalanceSheet, Balance, Transaction


##########################################################################
## Helper Functions
##########################################################################

def this_month(day=1):
    return date.today().replace(day=day)


##########################################################################
## Credit and Account Factories
##########################################################################

class CreditScoreFactory(factory.DjangoModelFactory):

    class Meta:
        model = CreditScore

    date = factory.Faker('date_this_decade')
    score = factory.fuzzy.FuzzyInteger(300, 850)
    source = factory.fuzzy.FuzzyChoice(CreditScore.BUREAUS, getter=lambda b: b[0])
    preferred = True
    memo = factory.Faker('sentence')


class CompanyFactory(factory.DjangoModelFactory):

    class Meta:
        model = Company
        django_get_or_create = ('name',)

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
        django_get_or_create = ('name',)

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
## Payments Factories
##########################################################################

def frequency_day_choice(obj):
    """
    Returns a day appropriate to the frequency of the object
    """
    if obj.frequency == Payment.WEEKLY:
        return random.choice(range(0, 7))
    elif obj.frequency == Payment.MONTHLY:
        return random.choice(range(0, 31))
    elif obj.frequency == Payment.QUARTERLY:
        return random.choice(range(0, 91))
    elif obj.frequency == Payment.YEARLY:
        return random.choice(range(0, 365))
    else:
        return None


class PaymentFactory(factory.DjangoModelFactory):

    class Meta:
        model = Payment

    description = None
    credit = factory.SubFactory(AccountFactory)
    debit = factory.SubFactory(BillingAccountFactory)
    frequency = factory.fuzzy.FuzzyChoice(Payment.FREQUENCY_TYPES, getter=lambda f: f[0])
    day = factory.LazyAttribute(frequency_day_choice)
    amount = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    active = True


class CreditCardPaymentFactory(PaymentFactory):

    credit = factory.SubFactory(CreditCardFactory)


##########################################################################
## Balance Sheet Factories
##########################################################################

class BalanceSheetFactory(factory.DjangoModelFactory):

    class Meta:
        model = BalanceSheet
        django_get_or_create = ('date',)

    date = factory.LazyFunction(this_month)
    memo = factory.Faker('sentence')


class BalanceFactory(factory.DjangoModelFactory):

    class Meta:
        model = Balance

    sheet = factory.SubFactory(BalanceSheetFactory)
    account = factory.SubFactory(AccountFactory)
    beginning = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)


class CreditCardBalanceFactory(BalanceFactory):

    account = factory.SubFactory(CreditCardFactory)
    beginning = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=False)


class TransactionFactory(factory.DjangoModelFactory):

    class Meta:
        model = Transaction

    sheet  = factory.SubFactory(BalanceSheetFactory)
    date   = factory.Faker('date_between_dates', date_start=this_month()-timedelta(days=15), date_end=this_month()+timedelta(days=15))
    credit = factory.SubFactory(AccountFactory)
    debit  = factory.SubFactory(CreditCardFactory)
    amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    memo   = factory.Faker('sentence')
    complete = factory.LazyAttribute(lambda o: o.date < o.sheet.date)
