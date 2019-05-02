# budget.models
# Budget app database models
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed May 01 21:25:21 2019 -0400
#
# Copyright (C) 2019 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: models.py [] benjamin@bengfort.com $

"""
Budget app database models
"""

##########################################################################
## Imports
##########################################################################

from datetime import date
from django.db import models


class Budget(models.Model):
    """
    A model for constructing a high-level overview of a budget for the year. This model
    is essentially a container for budget line items including income and expenses.
    """

    # Budgets are indexed by year
    year = models.PositiveSmallIntegerField(
        null=False, blank=False, unique=True, editable=True, default=date.today().year,
        help_text="Household fiscal year"
    )

    # Budget goals and description
    description = models.TextField(
        blank=True, null=False, default="", editable=True,
        help_text="Budget goals, notes, and general information"
    )

    class Meta:
        db_table = "budgets"
        ordering = ("-year",)

    def __str__(self):
        return "{} Budget".format(self.year)


class LineItem(models.Model):
    """
    A budget line is either income or an expense associated with a budget year. Budget
    lines can have frequency (e.g. 1 is anually, 12 is monthly, etc.) for ease of
    computation and recording.
    """

    budget = models.ForeignKey(
        'budget.Budget', on_delete=models.CASCADE, null=False,
        related_name="line_items", help_text="the budget to assign this line item to",
    )

    name = models.CharField(
        default=None, null=False, blank=False, max_length=255,
        help_text="Name of income or expense"
    )

    amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=False, null=False, default=0.0,
        help_text="Projected amount per period"
    )

    frequency = models.PositiveSmallIntegerField(
        blank=False, null=False, default=12,
        help_text="Number of times per year amount is paid"
    )

    is_income = models.BooleanField(
        default=False, help_text="Check if income source, uncheck if expense"
    )

    notes = models.CharField(
        default="", null=False, blank=True, max_length=512,
        help_text="Notes or other details about line item"
    )

    order = models.PositiveSmallIntegerField(
        default=None, null=True, blank=True,
        help_text="User defined order for display"
    )


    class Meta:
        db_table = "budget_line_items"
        ordering = ("-budget__year", "order")

    @property
    def is_expense(self):
        return not self.is_income

    @property
    def total(self):
        return self.frequency * self.amount

    @property
    def frequency_text(self):
        text = {
            1: "annually",
            4: "quarterly",
            12: "monthly",
            52: "weekly",
            24: "bimonthly",
            26: "biweekly",
            365: "daily",
        }.get(self.frequency, None)

        if text is None:
            return "{} times per year".format(self.frequency)
        return text

    def __str__(self):
        return "{} Budget: {}".format(self.budget.year, self.name)