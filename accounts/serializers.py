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
from .models import CreditScore
from .models import Account, Company, Payment
from .models import BalanceSheet, Balance, Transaction

from decimal import Decimal
from django.db.models import Count
from rest_framework import serializers


##########################################################################
## Account Serializers
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
## Payments Serializers
##########################################################################

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


##########################################################################
## Transaction Serializers
##########################################################################

class TransactionSerializer(serializers.ModelSerializer):

    credit = serializers.HyperlinkedRelatedField(
        view_name="api:accounts-detail",
        queryset=Account.objects.all()
    )

    debit = serializers.HyperlinkedRelatedField(
        view_name="api:accounts-detail",
        queryset=Account.objects.all()
    )

    class Meta:
        model = Transaction
        fields = ("id", "date", "credit", "debit", "amount", "complete", "memo",)

    def validate_amount(self, value):
        try:
            return Decimal(value)
        except TypeError as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        if "sheet" not in validated_data:
            raise KeyError("view must specify the sheet associated with the transaction")
        return super(TransactionSerializer, self).create(validated_data)


class TransactionSummarySerializer(TransactionSerializer):

    credit = AccountNameSerializer()
    debit = AccountNameSerializer()


class CreditTransactionSerializer(TransactionSerializer):

    # Assumes the target account is the credit account so retrieves the debit
    account = AccountNameSerializer(source="debit")
    amount = serializers.FloatField()

    class Meta(TransactionSerializer.Meta):
        fields = ("id", "account", "amount", "complete")


class DebitTransactionSerializer(TransactionSerializer):

    # Assumes the target account is the debit account so retrieves the credit
    account = AccountNameSerializer(source="credit")
    amount = serializers.FloatField()

    class Meta(TransactionSerializer.Meta):
        fields = ("id", "account", "amount", "complete")


##########################################################################
## Balance Serializers
##########################################################################

class BalanceSerializer(serializers.ModelSerializer):

    account = serializers.HyperlinkedRelatedField(
        view_name="api:accounts-detail",
        queryset=Account.objects.all()
    )

    # TODO: Be better with float vs decimal fields (e.g. use int with cents)
    beginning = serializers.FloatField(required=False)
    ending = serializers.FloatField(read_only=True)

    class Meta:
        model = Balance
        fields = ("id", "account", "beginning", "ending")

    def validate_beginning(self, value):
        try:
            return Decimal(value)
        except TypeError as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        if "sheet" not in validated_data:
            raise KeyError("view must specify the sheet associated with the balance")
        return super(BalanceSerializer, self).create(validated_data)


class BalanceSummarySerializer(BalanceSerializer):

    account = AccountNameSerializer()

    class Meta:
        model = Balance
        fields = ("id", "account", "beginning", "ending",)


class BalanceDetailSerializer(BalanceSerializer):

    account = AccountNameSerializer()
    credits = CreditTransactionSerializer(many=True)
    debits = DebitTransactionSerializer(many=True)
    credit_amount = serializers.SerializerMethodField()
    debit_amount = serializers.SerializerMethodField()
    credit_completed_amount = serializers.SerializerMethodField()
    debit_completed_amount = serializers.SerializerMethodField()
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


##########################################################################
## Balance Sheet Serializers
##########################################################################

class BalanceSheetSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = BalanceSheet
        fields = ("url", "date", "title", "memo")
        extra_kwargs = {
            "url": {"view_name": "api:sheets-detail", "lookup_field": "date"},
            "title": {"required": False, "default": None},
            "memo": {"required": False, "default": None},
        }

    def _sheet_exists_for_month(self, date):
        qs = BalanceSheet.objects.filter(date__year=date.year, date__month=date.month)
        return qs.count() > 0

    def create(self, data):
        """
        Ensure that a sheet is unique for month/year before create
        """
        if self._sheet_exists_for_month(data['date']):
            detail = "a balance sheet already exists for {}".format(
                data['date'].strftime("%b %Y")
            )
            raise serializers.ValidationError(detail=detail)
        return super(BalanceSheetSerializer, self).create(data)

    def update(self, instance, data):
        """
        Ensure sheet is unique for month/year before update
        """
        date = data['date']
        if instance.date.year != date.year or instance.date.month != date.month:
            if self._sheet_exists_for_month(date):
                detail = "cannot update sheet, a sheet already exists for {}".format(
                    date.strftime("%b %Y")
                )
                raise serializers.ValidationError(detail=detail)
        return super(BalanceSheetSerializer, self).update(instance, data)


class BalanceSheetSummarySerializer(BalanceSheetSerializer):
    """
    Gives summary information for the balance sheet, used in list views.
    """

    num_accounts = serializers.SerializerMethodField()
    num_transactions = serializers.SerializerMethodField()
    href = serializers.URLField(source="get_absolute_url", read_only=True)

    class Meta(BalanceSheetSerializer.Meta):
        fields = (
            "url", "date", "title", "memo", 'num_accounts', 'num_transactions', 'href',
        )

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


class BalanceSheetDetailSerializer(BalanceSheetSerializer):
    """
    Gives extended information for the balance sheet, used in detail views.
    """

    balances = BalanceSummarySerializer(many=True, read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta(BalanceSheetSerializer.Meta):
        fields = ("url", "date", "title", "memo", "balances", "transactions",)


##########################################################################
## Credit Score Serializers
##########################################################################

class CreditScoreSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CreditScore
        fields = ("url", "date", "score", "source")
        extra_kwargs = {
            "url": {"view_name": "api:creditscores-detail"}
        }
