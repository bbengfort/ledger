# budget.models.category
# Category models for the budget app.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Sep 29 15:03:47 2024 -0500
#
# Copyright (C) 2024 Bengfort.com
# For license information, see LICENSE
#
# ID: category.py [] benjamin@bengfort.com $

"""
Category models for the budget app.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models
from colorfield.fields import ColorField


class Category(models.Model):
    """
    A category class for grouping and aggregating subscriptions and other budget items.
    """

    name = models.CharField(
        default=None, null=False, blank=False, unique=True, max_length=128,
        help_text="Name of the category",
    )

    description = models.TextField(
        blank=True,
        null=False,
        default="",
        editable=True,
        help_text="Any notes or other information about the category",
    )

    color = ColorField(
        null=False,
        default='#CCCCCC',
        editable=True,
        help_text='The color to assign to the category in labels and bar charts',
    )

    active = models.BooleanField(
        default=True,
        help_text="Show the category in the active categories list",
    )

    exclude = models.BooleanField(
        default=False,
        help_text="Exclude any items from this category in overview and aggregations",
    )

    class Meta:
        db_table = "budget_categories"
        ordering = ("name",)
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
