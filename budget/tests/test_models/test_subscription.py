# budget.tests.test_models.test_subscription
# Model tests for the budget app.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Sep 23 07:52:04 2024 -0500
#
# Copyright (C) 2024 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_subscription.py [] benjamin@bengfort.com $

"""
Model tests for the budget app.
"""

##########################################################################
## Imports
##########################################################################

import pytest

from ..factories import *

# All tests in this module use the database
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "frequency,expected",
    [
        (1, "annually"),
        (4, "quarterly"),
        (12, "monthly"),
        (52, "weekly"),
        (24, "bimonthly"),
        (26, "biweekly"),
        (365, "daily"),
        (21, "21 times per year"),
    ],
)
def test_subscription_frequency_text(frequency, expected):
    assert SubscriptionFactory(frequency=frequency).frequency_text == expected


@pytest.mark.parametrize(
    "frequency,expected",
    [
        (1, 12.33),
        (4, 49.32),
        (12, 147.96),
        (52, 641.16),
        (24, 295.92),
        (26, 320.58),
        (365, 4500.45),
        (21, 258.93),
    ],
)
def test_subscription_total(frequency, expected):
    assert SubscriptionFactory(frequency=frequency, amount=12.33).total == expected
