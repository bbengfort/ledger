# accounts.admin
# Account admin configuration
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed May 02 15:40:33 2018 -0400
#
# ID: admin.py [0395481] benjamin@bengfort.com $

"""
Account admin configuration
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin
from .models import Account, Company, CreditScore
from .models import BalanceSheet, Balance, Transaction, Payment


##########################################################################
## Admin Configuration
##########################################################################

class BalanceInline(admin.TabularInline):

    extra = 0
    model = Balance
    fields = ('account', 'beginning')


class TransactionInline(admin.TabularInline):

    extra = 0
    model = Transaction
    fields = ('date', 'credit', 'debit', 'amount', 'complete')


class BalanceSheetAdmin(admin.ModelAdmin):
    # NOTE: this is no longer used as it was way too heavy-weight for editing
    # balance sheets. The balance sheet admin form took a long time to load and
    # when saving multiple changes to transactions and balances it would mess
    # them up and not save things correctly.
    #
    # See #19 for more details

    inlines = [
        BalanceInline, TransactionInline
    ]


##########################################################################
## Register your models here
##########################################################################

admin.site.register(Account)
admin.site.register(Company)
admin.site.register(Payment)
admin.site.register(BalanceSheet)
admin.site.register(Balance)
admin.site.register(Transaction)
admin.site.register(CreditScore)
