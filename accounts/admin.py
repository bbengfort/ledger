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

# Register your models here.
admin.site.register(Account)
admin.site.register(Company)
admin.site.register(BalanceSheet)
admin.site.register(Balance)
admin.site.register(Transaction)
