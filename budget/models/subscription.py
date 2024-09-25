# budget.models.subscription
# Subscription models for the budget app.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Sep 23 07:51:19 2024 -0500
#
# Copyright (C) 2024 Bengfort.com
# For license information, see LICENSE
#
# ID: subscription.py [] benjamin@bengfort.com $

"""
Subscription models for the budget app
"""

##########################################################################
## Imports
##########################################################################

from django.db import models


class Subscription(models.Model):
    """
    A model for tracking subscription costs that are not directly imported into a
    balance sheet. This model can be used for assessing different types of fixed,
    recurring costs for the budget.
    """

    name = models.CharField(
        default=None, null=False, blank=False, max_length=255,
        help_text="Name of subscription",
    )

    notes = models.TextField(
        blank=True, null=False, default="", editable=True,
        help_text="Any notes or other information about the subscription",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=False,
        null=False,
        default=0.0,
        help_text="Subscription cost",
    )

    frequency = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        default=12,
        help_text="Number of times per year amount is paid",
    )

    active = models.BooleanField(
        default=True,
        help_text="Show the subscription in the active subscriptions list",
    )

    exclude = models.BooleanField(
        default=False, help_text="Exclude subscription from overview and aggregations"
    )

    opened_on = models.DateField(
        null=True, blank=True, help_text="Date the subscription was opened"
    )

    closed_on = models.DateField(
        null=True, blank=True, help_text="Date the subscription was closed"
    )

    order = models.PositiveSmallIntegerField(
        default=None, null=True, blank=True, help_text="User defined order for display"
    )

    class Meta:
        db_table = "subscriptions"
        ordering = ("order", "-opened_on")
        get_latest_by = "opened_on"

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

    @property
    def total(self):
        return self.frequency * self.amount

    def __str__(self):
        return self.name
