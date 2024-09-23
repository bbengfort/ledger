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


def test_empty_subscription():
    SubscriptionFactory()
