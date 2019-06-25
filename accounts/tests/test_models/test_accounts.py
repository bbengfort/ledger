# accounts.tests.test_models.test_accounts
# Tests for account models
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Oct 04 20:04:03 2018 -0400
#
# ID: test_accounts.py [] benjamin@bengfort.com $

"""
Tests for account models
"""

##########################################################################
## Imports
##########################################################################

import pytest

from ..factories import AccountFactory
from accounts.models import Account

# All tests in this module use the database
pytestmark = pytest.mark.django_db


##########################################################################
## Account Tests
##########################################################################

class TestAccount(object):
    """
    Test the Account model
    """

    @pytest.mark.parametrize("account,expected", [
        (Account.CASH, False),
        (Account.CREDIT, True),
        (Account.LOAN, True),
        (Account.INVESTMENT, False),
        (Account.INSURANCE, False),
        (Account.BILLING, True),
    ])
    def test_is_liability(self, account, expected):
        """
        Check account type is liability
        """
        account = AccountFactory.build(type=account)
        assert account.is_liability is expected

    @pytest.mark.parametrize("account,expected", [
        (Account.CASH, True),
        (Account.CREDIT, False),
        (Account.LOAN, False),
        (Account.INVESTMENT, True),
        (Account.INSURANCE, True),
        (Account.BILLING, False),
    ])
    def test_is_asset(self, account, expected):
        """
        Check account type is asset
        """
        account = AccountFactory.build(type=account)
        assert account.is_asset is expected
