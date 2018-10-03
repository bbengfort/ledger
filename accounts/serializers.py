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

from .models import Account, BalanceSheet, Company, Balance, Transaction

from django.db.models import Count
from rest_framework import serializers


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


class BalanceSerializer(serializers.ModelSerializer):

    account = serializers.StringRelatedField()

    class Meta:
        model = Balance
        fields = ("id", "account", "beginning", "ending",)


class TransactionSerializer(serializers.ModelSerializer):

    credit = serializers.StringRelatedField()
    debit = serializers.StringRelatedField()

    class Meta:
        model = Transaction
        fields = ("id", "date", "credit", "debit", "amount", "complete", "memo",)


class BalanceSheetDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    Gives extended information for the balance sheet, used in detail views.
    """

    balances = BalanceSerializer(many=True, read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = BalanceSheet
        fields = ("url", "date", "title", "memo", "balances", "transactions",)
        extra_kwargs = {
            "url": {"view_name": "api:sheets-detail", "lookup_field": "date"},
        }


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
