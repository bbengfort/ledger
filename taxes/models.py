# taxes.models
# Tax models
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 16:36:54 2018 -0400
#
# ID: models.py [] benjamin@bengfort.com $

"""
Tax models
"""

##########################################################################
## Imports
##########################################################################

from django.db import models


class TaxReturn(models.Model):
    """
    A model for data reported on IRS form 1040
    """

    # Tax returns are indexed by year
    year = models.PositiveSmallIntegerField(
        help_text="Tax year the return was filed for"
    )

    # Income related fields
    wages = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Wages, salaries and tips",
    )
    interest = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=0.0,
        help_text="Interest, taxable and tax-exempt combined",
    )
    profit = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=0.0,
        help_text="Business income (or loss)"
    )
    dividends = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=0.0,
        help_text="Ordinary and qualified dividends"
    )
    capital_gains = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=0.0,
        help_text="Capital gains (or loss)"
    )
    royalties = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=0.0,
        help_text="Rental real estate, royalties, partnerships, etc"
    )
    income = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Total reported income including other fields"
    )
    agi = models.DecimalField(
        "adjusted gross income", max_digits=10, decimal_places=2,
        help_text="Adjusted gross income after non-taxable income removed"
    )
    taxable_income = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Taxable income after itemized deductions"
    )

    # Tax related fields
    federal_tax = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Total amount owed or paid in Federal taxes",
    )
    local_tax = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Total amount owed or paid in state and local taxes",
    )


    def __str__(self):
        return "Tax Year {}".format(self.year)
