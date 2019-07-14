# accounts.serializers
# Data serialization for the JSON API
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed Oct 03 10:40:40 2018 -0400
#
# ID: serializers.py [] benjamin@bengfort.com $

"""
Data serialization for the JSON API
"""

##########################################################################
## Imports
##########################################################################

from .utils import Currency
from .models import Account, Company, Payment
from .models import BalanceSheet, Balance, Transaction

from django.db.models import Count
from rest_framework import serializers


##########################################################################
## Model Serializers
##########################################################################

class BankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ("name", "short_name", "url")


class AccountSerializer(serializers.HyperlinkedModelSerializer):

    bank = BankSerializer()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ("url", "type", "name", "number", "opened_on", "closed_on", "bank",)
        extra_kwargs = {
            "url": {"view_name": "api:accounts-detail"}
        }

    def get_type(self, obj):
        return obj.get_type_display()


class AccountNameSerializer(serializers.HyperlinkedModelSerializer):

    name = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ("url", "name")
        extra_kwargs = {
            "url": {"view_name": "api:accounts-detail"}
        }

    def get_name(self, obj):
        return str(obj)


##########################################################################
## Balance Sheet Serializers
##########################################################################

class BalanceSheetShortSerializer(serializers.HyperlinkedModelSerializer):
    """
    Gives summary information for the balance sheet, used in list views.
    """

    num_accounts = serializers.SerializerMethodField()
    num_transactions = serializers.SerializerMethodField()

    class Meta:
        model = BalanceSheet
        fields = (
            "url", "date", "title", "memo", 'num_accounts', 'num_transactions',
        )
        extra_kwargs = {
            "url": {"view_name": "api:sheets-detail", "lookup_field": "date"}
        }

    def get_num_accounts(self, obj):
        # NOTE: the order_by is required or this won't group account types
        data = obj.accounts.values('type').annotate(count=Count('type')).order_by()

        # Flatten the data into a type:count dictionary
        # TODO: this is probably poor performance to create the dict every time
        types = dict(Account.ACCOUNT_TYPES)
        return {
            types[item["type"]]: item["count"]
            for item in data
        }

    def get_num_transactions(self, obj):
        return obj.transactions.count()


class TransactionSerializer(serializers.ModelSerializer):

    credit = AccountNameSerializer()
    debit = AccountNameSerializer()

    class Meta:
        model = Transaction
        fields = ("id", "date", "credit", "debit", "amount", "complete", "memo",)


class PaymentSerializer(serializers.ModelSerializer):

    credit = serializers.StringRelatedField()
    debit = serializers.StringRelatedField()
    description = serializers.SerializerMethodField()
    frequency = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ("id", "description", "frequency", "amount", "credit", "debit")

    def get_description(self, obj):
        return str(obj)

    def get_frequency(self, obj):
        return obj.get_frequency_display()


class CreditTransactionSerializer(serializers.ModelSerializer):

    # Assumes the target account is the credit account so retrieves the debit
    account = AccountNameSerializer(source="debit")
    amount = serializers.FloatField()

    class Meta:
        model = Transaction
        fields = ("id", "account", "amount", "complete")


class DebitTransactionSerializer(serializers.ModelSerializer):

    # Assumes the target account is the debit account so retrieves the credit
    account = AccountNameSerializer(source="credit")
    amount = serializers.FloatField()

    class Meta:
        model = Transaction
        fields = ("id", "account", "amount", "complete")


class BalanceSummarySerializer(serializers.ModelSerializer):

    account = AccountNameSerializer()
    beginning = serializers.FloatField()
    ending = serializers.FloatField()

    class Meta:
        model = Balance
        fields = ("id", "account", "beginning", "ending",)


class BalanceDetailSerializer(serializers.ModelSerializer):

    account = AccountNameSerializer()
    credits = CreditTransactionSerializer(many=True)
    debits = DebitTransactionSerializer(many=True)
    credit_amount = serializers.SerializerMethodField()
    debit_amount = serializers.SerializerMethodField()
    credit_completed_amount = serializers.SerializerMethodField()
    debit_completed_amount = serializers.SerializerMethodField()
    beginning = serializers.FloatField()
    ending = serializers.FloatField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Balance
        fields = (
            "id", "account", "beginning", "ending", "currency",
            "credits", "debits", "credit_amount", "debit_amount",
            "credit_completed_amount", "debit_completed_amount",
        )

    def get_credit_amount(self, obj):
        return obj.credit_amount(completed=False)

    def get_credit_completed_amount(self, obj):
        return obj.credit_amount(completed=True)

    def get_debit_amount(self, obj):
        return obj.debit_amount(completed=False)

    def get_debit_completed_amount(self, obj):
        return obj.debit_amount(completed=True)

    def get_currency(self, obj):
        return Currency[obj.account.currency].symbol


class BalanceSheetDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    Gives extended information for the balance sheet, used in detail views.
    """

    balances = BalanceSummarySerializer(many=True, read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = BalanceSheet
        fields = ("url", "date", "title", "memo", "balances", "transactions",)
        extra_kwargs = {
            "url": {"view_name": "api:sheets-detail", "lookup_field": "date"},
        }


