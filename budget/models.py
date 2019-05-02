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
from decimal import Decimal
from django.db import models
from django.urls import reverse


class Budget(models.Model):
    """
    A model for constructing a high-level overview of a budget for the year. This model
    is essentially a container for budget line items including income and expenses.
    """

    # Budgets are indexed by year
    year = models.PositiveSmallIntegerField(
        unique=True, default=date.today().year,
        null=False, blank=False, editable=True,
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
        get_latest_by = "year"

    def get_absolute_url(self):
        kwargs = {'year': self.year}
        return reverse('budget-detail', kwargs=kwargs)

    def income_items(self):
        return self.line_items.filter(is_income=True)

    def total_income(self):
        return sum(item.total for item in self.income_items())

    def monthly_income(self):
        amt = Decimal(self.total_income() / 12)
        return round(amt, 2)

    def expense_items(self):
        return self.line_items.filter(is_income=False)

    def total_expenses(self):
        return sum(item.total for item in self.expense_items())

    def monthly_expenses(self):
        amt =  Decimal(self.total_expenses() / 12)
        return round(amt, 2)

    def monthly_savings(self):
        return self.monthly_income() - self.monthly_expenses()

    def total_savings(self):
        return self.total_income() - self.total_expenses()

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