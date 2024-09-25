# budget.tests.test_models.test_budget
# Model tests for the budget app.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu May 02 10:57:56 2019 -0400
#
# Copyright (C) 2019 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_budget.py [] benjamin@bengfort.com $

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


def test_empty_budget():
    b = BudgetFactory()
    assert b.income_items().count() == 0
    assert b.expense_items().count() == 0
    assert b.total_income() == 0
    assert b.monthly_income() == 0
    assert b.total_expenses() == 0
    assert b.monthly_expenses() == 0
    assert b.monthly_savings() == 0
    assert b.total_savings() == 0
