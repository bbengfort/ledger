# accounts.tests.test_models
# Tests for account models
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Oct 04 20:04:03 2018 -0400
#
# ID: test_models.py [] benjamin@bengfort.com $

"""
Tests for account models
"""

##########################################################################
## Imports
##########################################################################

import pytest

from .factories import *
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


##########################################################################
## Test Credit Score
##########################################################################

@pytest.mark.parametrize("score, description, percent", [
    (800, "Exceptional", 94.11764705882352),
    (760, "Very Good", 89.41176470588236),
    (710, "Good", 83.52941176470588),
    (623, "Fair", 73.29411764705883),
    (423, "Very Poor", 49.76470588235294),
])
def test_credit_score(score, description, percent):
    """
    Test credit score properties with a variety of scores
    """
    score = CreditScoreFactory(score=score)
    assert score.description == description
    assert score.percent == percent
