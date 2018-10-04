# accounts.models.credit
# Credit Score tracking model.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Oct 04 08:08:59 2018 -0400
#
# ID: credit.py [] benjamin@bengfort.com $

"""
Credit Score tracking model.
"""

##########################################################################
## Imports
##########################################################################

from datetime import date

from django.db import models


##########################################################################
## Credit Score
##########################################################################

class CreditScore(models.Model):
    """
    A record of credit scores tracked over time by a variety of sources.
    Ideally there are three credit score reports per month, though it usually
    costs money to get a credit score report. Becasue of this, the model is
    purposefully lightweight to support many possible credit score iterations
    over a long period of time.
    """

    EXPERIAN   = "Experian"
    EQUIFAX    = "Equifax"
    TRANSUNION = "TransUnion"

    BUREAUS = (
        (EXPERIAN, EXPERIAN),
        (EQUIFAX, EQUIFAX),
        (TRANSUNION, TRANSUNION),
    )

    date = models.DateField(
        null=False, blank=False, default=date.today,
        help_text="Date of credit score report"
    )
    score = models.PositiveSmallIntegerField(
        null=False, blank=False,
        help_text="Credit score between 0 and 850"
    )
    source = models.CharField(
        max_length=255, blank=False, null=False, choices=BUREAUS,
        help_text="The credit bureau that generated the report",
    )
    preferred = models.BooleanField(
        default=True,
        help_text="If this score should be used over others in the month"
    )
    memo = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="A short memo or note about the credit score",
    )

    class Meta:
        db_table = "credit_scores"
        ordering = ("-date",)
        get_latest_by = "date"

    def __str__(self):
        return "{} by {} on {}".format(
            self.score, self.source, self.date
        )

    @property
    def description(self):
        """
        Returns a textual description of the score.
        Source: https://www.experian.com/blogs/ask-experian/credit-education/score-basics/what-is-a-good-credit-score/
        """
        if self.score >= 800:
            # 20% of Americans
            return "Exceptional"

        if self.score >= 740:
            # 25% of Americans
            return "Very Good"

        if self.score >= 670:
            # 21% of Americans
            return "Good"

        if self.score >= 580:
            # 18% of Americans
            return "Fair"

        # 16% of Americans
        return "Very Poor"

    @property
    def percent(self):
        """
        Returns the percentage of the maximum score.
        """
        return (float(self.score) / 850.0) * 100
