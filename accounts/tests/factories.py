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
import factory.django

from datetime import date, timedelta
from django.contrib.auth.models import User

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
## User Factories
##########################################################################

class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Faker('user_name')
    password = factory.Faker('password')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Users must be created with the `create_user` command so that the
        password is correctly set with the secret key.

        For more information, see:
        https://docs.djangoproject.com/en/dev/topics/testing/tools/#django.test.Client.login
        """
        manager = cls._get_manager(model_class)
        user = manager.create_user(*args, **kwargs)

        # Ensure the password is in plaintest
        user.password = kwargs['password']
        return user


class AdminUserFactory(UserFactory):

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Uses create_superuser to create the admin
        manager = cls._get_manager(model_class)
        user = manager.create_superuser(*args, **kwargs)

        # Ensure the password is in plaintest
        user.password = kwargs['password']
        return user


##########################################################################
## Credit and Account Factories
##########################################################################

class CreditScoreFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = CreditScore

    date = factory.Faker('date_this_decade')
    score = factory.fuzzy.FuzzyInteger(300, 850)
    source = factory.fuzzy.FuzzyChoice(CreditScore.BUREAUS, getter=lambda b: b[0])
    preferred = True
    memo = factory.Faker('sentence')


class CompanyFactory(factory.django.DjangoModelFactory):

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


class AccountFactory(factory.django.DjangoModelFactory):

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


class CharitableAccountFactory(AccountFactory):

    type = Account.CHARITABLE
    name = "Church Tithe"


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
        return random.choice(range(0, 32))
    elif obj.frequency == Payment.QUARTERLY:
        return random.choice((1, 15, 31, 32, 46, 62, 63, 77, 93))
    elif obj.frequency == Payment.YEARLY:
        return random.choice(range(0, 366))
    else:
        return None


class PaymentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Payment

    description = ""
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

class BalanceSheetFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = BalanceSheet
        django_get_or_create = ('date',)

    date = factory.LazyFunction(this_month)
    memo = factory.Faker('sentence')


class BalanceFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Balance

    sheet = factory.SubFactory(BalanceSheetFactory)
    account = factory.SubFactory(AccountFactory)
    beginning = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)


class CreditCardBalanceFactory(BalanceFactory):

    account = factory.SubFactory(CreditCardFactory)
    beginning = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=False)


class TransactionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Transaction

    sheet = factory.SubFactory(BalanceSheetFactory)
    date = factory.Faker('date_between_dates', date_start=this_month()-timedelta(days=15), date_end=this_month()+timedelta(days=15))
    credit = factory.SubFactory(AccountFactory)
    debit = factory.SubFactory(CreditCardFactory)
    amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    memo = factory.Faker('sentence')
    complete = factory.LazyAttribute(lambda o: o.date < o.sheet.date)
