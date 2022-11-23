# budget.tests.test_views
# Test the budget views module
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu May 02 11:12:05 2019 -0400
#
# Copyright (C) 2019 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_views.py [] benjamin@bengfort.com $

"""
Test the budget views module
"""

##########################################################################
## Imports
##########################################################################

from .factories import BudgetFactory


def test_no_budget(admin_client):
    """
    LatestBudget should return a 404 when there is no latest budget with logged in user.
    """
    response = admin_client.get("/budget/")
    assert response.status_code == 404


def test_latest_budget(admin_client):
    """
    LatestBudget should return latest budget with logged in user.
    """
    # Create the budget
    prev_budget = BudgetFactory(year=1999)
    budget = BudgetFactory()

    response = admin_client.get("/budget/")
    assert response.status_code == 302
    assert response.url != prev_budget.get_absolute_url()
    assert response.url == budget.get_absolute_url()
