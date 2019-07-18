# accounts.views.api
# API ViewSets and controllers
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed Oct 03 10:30:01 2018 -0400
#
# ID: api.py [] benjamin@bengfort.com $

"""
API ViewSets and controllers
"""

##########################################################################
## Imports
##########################################################################

from django.db import connection

from ..models import Account, Payment
from ..models import BalanceSheet, Balance, Transaction
from ..serializers import BalanceSerializer
from ..serializers import AccountSerializer
from ..serializers import PaymentSerializer
from ..serializers import BalanceSheetDetailSerializer
from ..serializers import BalanceSheetSummarySerializer
from ..serializers import BalanceDetailSerializer, BalanceSummarySerializer
from ..serializers import TransactionSerializer, TransactionSummarySerializer

from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound


__all__ = [
    "AccountViewSet", "BalanceSheetViewSet",
    "BalanceViewSet", "TransactionViewSet",
    "PaymentsAPIView", "CashFlow",
]


##########################################################################
## Basic Resources
##########################################################################

class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Display account and bank information
    """

    queryset = Account.objects.filter(active=True)
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAdminUser]


##########################################################################
## BalanceSheet Base Resource
##########################################################################

class BalanceSheetViewSet(viewsets.ModelViewSet):
    """
    Most viewsets are nested under their associated balance sheet.
    """

    queryset = BalanceSheet.objects.all()
    lookup_field = 'date'
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        """
        Returns list or detail balance sheet serializers
        """
        if self.action in {'list', 'create'}:
            return BalanceSheetSummarySerializer
        return BalanceSheetDetailSerializer


##########################################################################
## Balance Sheet Nested Resources
##########################################################################

class BalanceSheetNestedResource(viewsets.ModelViewSet):

    model_class = None

    def get_model_class(self):
        assert self.model_class is not None, (
            "'%s' should either include a `model_class` attribute, "
            "or override the `get_model_class()` method."
            % self.__class__.__name__
        )

        return self.model_class

    def get_queryset(self):
        sheet_date = self.kwargs['sheet_date']
        if not BalanceSheet.objects.filter(date=sheet_date).exists():
            raise NotFound("balance sheet for {} not found".format(sheet_date))
        return self.get_model_class().objects.filter(sheet__date=sheet_date)

    def create(self, request, sheet_date=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            sheet = BalanceSheet.objects.get(date=sheet_date)
        except BalanceSheet.DoesNotExist:
            raise NotFound("balance sheet for {} not found".format(sheet_date))

        serializer.save(sheet=sheet)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )


class BalanceViewSet(BalanceSheetNestedResource):
    """
    Account balances associated with a balance sheet
    """

    model_class = Balance
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        """
        Returns the correct balance serializer based on the action
        """
        if self.action == "list":
            return BalanceSummarySerializer
        elif self.action in {"create", "update"}:
            return BalanceSerializer
        return BalanceDetailSerializer


class TransactionViewSet(BalanceSheetNestedResource):
    """
    Transactions associated with a balance sheet
    """

    model_class = Transaction
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        """
        Returns the correct transaction serializer based on the action
        """
        if self.action in {"create", "update"}:
            return TransactionSerializer
        return TransactionSummarySerializer


class PaymentsAPIView(viewsets.ModelViewSet):
    """
    Programmatically interact with payments and create transactions from them.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=["get"])
    def transaction(self, request, pk=None):
        payment = self.get_object()
        serializer = TransactionSummarySerializer(
            Transaction.from_payment(payment), context={'request': request}
        )
        return Response(serializer.data)


##########################################################################
## Data Views for Visualizations
##########################################################################

class CashFlow(viewsets.ViewSet):
    """
    Provides a cash vs. credit card debt listing for the past 6 months.
    """

    # TODO: move this to a SQL file that can be loaded on demand
    QUERY = (
        "WITH sheet_balances AS ("
        "	SELECT b.beginning, b.ending, s.id AS sheet_id, s.date, a.type FROM balances b"
        "		JOIN balance_sheets s ON b.sheet_id = s.id"
        "		JOIN accounts a ON b.account_id = a.id"
        "     WHERE a.active = 't' AND a.exclude = 'f'"
        "	ORDER BY s.date DESC"
        "), cash AS ("
        "	SELECT SUM(beginning) as beginning, SUM(ending) as ending, date FROM sheet_balances WHERE type = 'Ca' GROUP BY date"
        "), debt AS ("
        "	SELECT SUM(beginning) as beginning, SUM(ending) as ending, date FROM sheet_balances WHERE type = 'Cc' GROUP BY date"
        ")"

        "SELECT cash.date, cash.beginning AS cash_beginning, debt.beginning AS debt_beginning, "
        "	cash.ending AS cash_ending, debt.ending AS debt_ending, "
        "	cash.ending-cash.beginning AS cash_change, debt.ending-debt.beginning AS debt_change,"
        "	cash.beginning + debt.beginning AS net_beginning, cash.ending + debt.ending AS net_ending,"
        "	((cash.beginning+debt.beginning) - (cash.ending+debt.ending)) AS net_change"
        " FROM cash JOIN debt ON cash.date=debt.date"
        " ORDER BY cash.date DESC"
        " LIMIT 6"
    )

    def list(self, request):
        """
        Prepare the response for the past 6 months.
        """
        with connection.cursor() as cursor:
            # Execute the large query
            cursor.execute(self.QUERY)
            columns = [col[0] for col in cursor.description]

            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response(data)
