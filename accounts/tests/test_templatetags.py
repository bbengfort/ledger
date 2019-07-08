# accounts.tests.test_templatetags
# Test the template tag utilities using simple Django templates
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sun Oct 07 14:58:14 2018 -0400
#
# ID: test_templatetags.py [] benjamin@bengfort.com $

"""
Test the template tag utilities using simple Django templates
"""

##########################################################################
## Imports
##########################################################################

import pytest

from django.test import SimpleTestCase
from django.template import Context, Template

from accounts.templatetags.accounting import *


@pytest.mark.parametrize("amount, currency, expected", [
    (81.52, "USD", {"currency": "$", "balance": "81.52"}),
    (8614.59, "USD", {"currency": "$", "balance": "8,614.59"}),
    (0, "USD", {"currency": "$", "balance": "&mdash;"}),
    (None, "USD", {"currency": "$", "balance": "&mdash;"}),
    (-81.52, "USD", {"currency": "$", "balance": "(81.52)"}),
    (-8614.59, "USD", {"currency": "$", "balance": "(8,614.59)"}),
    (8614.59, "GBP", {"currency": "£", "balance": "8,614.59"}),
])
def test_accounting_amount(amount, currency, expected):
    """
    accounting_amount should return context for accounting display
    """
    assert accounting_amount(amount, currency) == expected


@pytest.mark.parametrize("before,after,expected", [
    (49.20, 100.10, '<big><i class="fa fa-caret-up text-success"></i></big>'),
    (100.10, 49.20, '<big><i class="fa fa-caret-down text-danger"></i></big>'),
    (53.50, 53.50, '<big><i class="fa fa-caret-right text-muted"></i></big>'),
    (None, None, '<big><i class="fa fa-caret-right text-muted"></i></big>'),
])
def test_direction(before, after, expected):
    """
    direction should return an icon indicating if after is bigger or smaller
    """
    assert direction(before, after) == expected


class TestAccountingTags(SimpleTestCase):
    """
    Test the accounting template tags
    """

    def test_accounting(self):
        """
        Test the accounting inclusion tag
        """
        template = Template(
            '{% load accounting %}'
            '{% accounting 23.22 %}'
            '{% accounting -3922.12 %}'
            '{% accounting 473.23 "GBP" %}'
        )

        rendered = template.render(Context({}))
        self.assertInHTML('<span class="pull-left">$</span>', rendered)
        self.assertInHTML('<span class="pull-right">23.22</span>', rendered)
        self.assertInHTML('<span class="pull-right">(3,922.12)</span>', rendered)
        self.assertInHTML('<span class="pull-left">£</span>', rendered)

    @pytest.mark.skip(reason="needs implementation")
    def test_account_balance(self):
        """
        Test the account_balance inclusion tag
        """
        pass

    @pytest.mark.skip(reason="needs implementation")
    def test_transaction_amount(self):
        """
        Test the transaction_amount inclusion tag
        """
        pass

    @pytest.mark.skip(reason="needs implementation")
    def test_transaction_credit(self):
        """
        Test the transaction_credit inclusion tag
        """
        pass

    def test_print_button(self):
        """
        Test the print_button inclusion tag
        """
        template = Template('{% load buttons %}{% print_button %}')
        rendered = template.render(Context({}))
        # self.assertInHTML('<a href="?print=True">', rendered)
        self.assertInHTML('<i class="fa fa-print">', rendered)

    def test_edit_button(self):
        """
        Test the edit_button inclusion tag
        """
        template = Template('{% load buttons %}{% edit_button %}')
        rendered = template.render(Context({}))
        self.assertInHTML('<i class="fa fa-edit">', rendered)

    @pytest.mark.skip(reason="needs implementation")
    def test_next_sheet(self):
        """
        Test the next_sheet inclusion tag
        """
        pass
