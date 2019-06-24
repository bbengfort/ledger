# accounts.models.payments
# Payments and billings related models.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jun 24 07:04:32 2019 -0400
#
# ID: payments.py [] benjamin@bengfort.com $

"""
Payments and billings related models.
"""

##########################################################################
## Imports
##########################################################################

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


##########################################################################
## Routine Payments and Recurring Transactions
##########################################################################

class Payment(models.Model):
    """
    A Payment is a associated with a billing account and stores details
    about routine or recurring payments, it is intended to help facilitate
    the quick creation of transactions. For example, if every month you pay
    a utility payment from a specific credit card, the payment will allow
    you to easily generate the transaction without having to remember which
    accounts the recurring payment is from.
    """

    # Payment Frequency
    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"
    QUARTERLY = "Q"
    YEARLY = "Y"
    INFREQUENT = "F"

    FREQUENCY_TYPES = (
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
        (MONTHLY, "Monthly"),
        (QUARTERLY, "Quarterly"),
        (YEARLY, "Yearly"),
        (INFREQUENT, "Infrequent"),
    )

    description = models.CharField(
        null=False,
        blank=True,
        default="",
        max_length=255,
        help_text="Short description for the payment",
    )

    credit = models.ForeignKey(
        "accounts.Account",
        null=False,
        on_delete=models.CASCADE,
        related_name="payment_sources",
        help_text="The source of funds for the payment",
    )

    debit = models.ForeignKey(
        "accounts.Account",
        null=False,
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="The destination of funds for the payment",
    )

    frequency = models.CharField(
        max_length=1,
        default=MONTHLY,
        choices=FREQUENCY_TYPES,
        help_text="The frequency of the payment",
    )

    day = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(366)],
        help_text="Day of week, month, quarter, or year the payment occurs on",
    )

    amount = models.DecimalField(
        null=True,
        blank=True,
        default=None,
        max_digits=10,
        decimal_places=2,
        help_text="The default amount of the recurring payment",
    )

    active = models.BooleanField(
        default=True,
        help_text="Show the payment in the active payments list",
    )

    class Meta:
        db_table = "payments"
        ordering = ("debit__name", "description")

    def transactions(self):
        """
        Returns the transactions related to this payment; e.g. all of the
        transactions between the credit and debit accounts. This model
        currently assumes that there is a unique together relationship
        between the credit and debit accounts (though this is not
        specified via a constraint); in the future if this is not true
        then some other database marker would be required.
        """
        return self.debit.debits.filter(credit=self.credit)

    def __str__(self):
        if self.description:
            return self.description

        if self.frequency != self.INFREQUENT:
            if self.amount:
                return "{}{} {} payments from {} to {}".format(
                    self.debit.get_currency_enum().symbol,
                    self.amount,
                    self.get_frequency_display().lower(),
                    self.credit,
                    self.debit,
                )
            return "{} payments from {} to {}".format(
                self.get_frequency_display(),
                self.credit,
                self.debit,
            )

        return "Payments from {} to {}".format(self.credit, self.debit)