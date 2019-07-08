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

from ..models import Account, BalanceSheet, Balance, Transaction
from ..serializers import AccountSerializer
from ..serializers import BalanceSheetShortSerializer
from ..serializers import BalanceSheetDetailSerializer
from ..serializers import TransactionSerializer
from ..serializers import BalanceDetailSerializer, BalanceSummarySerializer

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response


__all__ = [
    "AccountViewSet", "BalanceSheetViewSet",
    "BalanceViewSet", "TransactionViewSet",
    "CashFlow",
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

class BalanceSheetViewSet(viewsets.ReadOnlyModelViewSet):
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
        if self.action == 'list':
            return BalanceSheetShortSerializer
        return BalanceSheetDetailSerializer


##########################################################################
## Balance Sheet Nested Resources
##########################################################################

class BalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Account balances associated with a balance sheet
    """

    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Balance.objects.filter(sheet__date=self.kwargs['sheets_date'])

    def get_serializer_class(self):
        """
        Returns list or detail balance serializers
        """
        if self.action == "list":
            return BalanceSummarySerializer
        return BalanceDetailSerializer


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Transactions associated with a balance sheet
    """

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Transaction.objects.filter(sheet__date=self.kwargs['sheets_date'])


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
