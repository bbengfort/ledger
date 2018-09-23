# accounts.templatetags.accounting
# Accounting display related template tags and filters.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jun 05 11:45:29 2018 -0400
#
# ID: accounting.py [61ff136] benjamin@bengfort.com $

"""
Accounting display related template tags and filters.
"""

##########################################################################
## Imports
##########################################################################

from django import template
from django.utils.html import mark_safe
from accounts.utils import Currency


# Register template tags
register = template.Library()


def accounting_amount(amount, currency="USD"):
    if amount < 0:
        amount = "({:,})".format(amount * -1)
    elif amount == 0:
        amount = mark_safe("&mdash;")
    else:
        amount = "{:,}".format(amount)

    return {
        "currency": Currency[currency].symbol,
        "balance": amount,
    }


@register.inclusion_tag("snippets/account_balance.html")
def account_balance(balance, beginning=False, ending=False):
    if beginning:
        amount = balance.beginning
    elif ending:
        amount = balance.ending
    else:
        raise ValueError("please specify either beginning or ending balance")

    return accounting_amount(amount, balance.account.currency)


@register.inclusion_tag("snippets/account_balance.html")
def transaction_amount(transaction):
    return accounting_amount(transaction.amount, transaction.credit.currency)


@register.inclusion_tag("snippets/account_balance.html")
def accounting(amount, currency="USD"):
    return accounting_amount(amount, currency)


@register.inclusion_tag("components/print.html")
def print_button():
    return {}
