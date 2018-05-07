# accounts.admin
# Account admin configuration
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed May 02 15:40:33 2018 -0400
#
# ID: admin.py [] benjamin@bengfort.com $

"""
Account admin configuration
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin
from .models import Account, Company
from .models import BalanceSheet, Balance, Transaction


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

    inlines = [
        BalanceInline, TransactionInline
    ]


##########################################################################
## Register your models here
##########################################################################

admin.site.register(Account)
admin.site.register(Company)
admin.site.register(BalanceSheet, BalanceSheetAdmin)
admin.site.register(Balance)
admin.site.register(Transaction)
