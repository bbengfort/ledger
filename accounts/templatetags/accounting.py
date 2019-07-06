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

from datetime import date
from dateutil.relativedelta import relativedelta

from django import template
from django.conf import settings
from django.utils.html import mark_safe
from accounts.utils import Currency
from accounts.models import BalanceSheet


# Register template tags
register = template.Library()


def accounting_amount(amount, currency="USD"):
    # Database may return None instead of 0, handle here
    if amount is None:
        amount = 0

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
def accounting(value, currency="USD"):
    return accounting_amount(value, currency)


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
def transaction_credit(transaction):
    return accounting_amount(-1*transaction.amount, transaction.credit.currency)


@register.inclusion_tag("snippets/next_sheet.html")
def next_sheet():
    # If today is after the 15th of the month, then next month is the first
    # of the next month, if it is before, it is today's date.
    today = date.today()
    if today.day <= settings.BILLING_DAY_OF_MONTH:
        next_month = today
    else:
        next_month = (today + relativedelta(months=1)).replace(day=1)

    return {
        "latest": BalanceSheet.objects.get_current(raise_on_error=False),
        "next_month": next_month,
    }


@register.simple_tag()
def direction(before, after):
    # Database may return None instead of 0, handle here
    if before is None:
        before = 0

    if after is None:
        after = 0

    # Compute difference
    delta = after - before

    if delta > 0:
        icon = '<big><i class="fa fa-caret-up text-success"></i></big>'
    elif delta == 0:
        icon = '<big><i class="fa fa-caret-right text-muted"></i></big>'
    else:
        icon = '<big><i class="fa fa-caret-down text-danger"></i></big>'

    return mark_safe(icon)
