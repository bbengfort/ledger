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

from ..models import Account, BalanceSheet, Balance, Transaction
from ..serializers import AccountSerializer
from ..serializers import BalanceSheetShortSerializer
from ..serializers import BalanceSheetDetailSerializer
from ..serializers import BalanceSerializer, TransactionSerializer

from rest_framework import viewsets
from rest_framework import permissions


__all__ = [
    "AccountViewSet", "BalanceSheetViewSet",
    "BalanceViewSet", "TransactionViewSet",
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
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        """
        Returns list for detail balance sheet serializers
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

    serializer_class = BalanceSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Balance.objects.filter(sheet=self.kwargs['sheets_pk'])


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Transactions associated with a balance sheet
    """

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Transaction.objects.filter(sheet=self.kwargs['sheets_pk'])
