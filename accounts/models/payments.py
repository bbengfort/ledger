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

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator


__all__ = [
    "Payment"
]


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

    def get_api_url(self, action=None):
        kwargs = {'pk': self.id}

        if action is None:
            return reverse('api:payments-detail', kwargs=kwargs)

        if action == "transaction":
            return reverse('api:payments-transaction', kwargs=kwargs)

        raise ValueError("unknown API action '{}'".format(action))

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

    def next_payment_date(self, after=None):
        """
        Based on the frequency, returns the next payment date after the
        specified date. If after is None, then the next payment after today is
        computed. Note that after can be specified as a "%Y-%m-%d" string.

        This is a fairly complex function that depends on relative deltas and
        may have different behavior depending on the frequency. Roughly, the
        next payment date is computed as follows (by default):

        DAILY: return 1 day after today

        WEEKLY: return the next weekday where Monday=0 and Sunday=6 after today

        MONTHLY: if day in month is in future return it, otherwise return day
            next month. Note this truncates 31 to 30, 29, 28, etc.

        QUARTERLY: can only specify 1, 15, 31, 32, 46, 62, 63, 77, or 93 as
            the day; returns the 1st, 15th, or last day of the month for the
            specified quarter if it is in the future, or the next quarter.

        YEARLY: if the day in year is in future return it, otherwise retun
            day next year. This works poorly for leap years.
        """
        if after is None:
            after = date.today()
        elif isinstance(after, str):
            after = datetime.strptime(after, "%Y-%m-%d").date()

        # Always return tomorrow for daily frequency
        if self.frequency == self.DAILY:
            return after + relativedelta(days=1)

        # Return the next
        if self.frequency == self.WEEKLY:
            if self.day is None or self.day > 6:
                raise ValueError("weekly frequency requires day of week in range 0-6")

            delta = ((self.day - after.weekday() - 1) % 7) + 1
            return after + relativedelta(days=delta)

        if self.frequency == self.MONTHLY:
            if self.day is None or self.day > 31 or self.day < 1:
                raise ValueError(
                    "monthly frequency requires day of month in range 1-31"
                )
            months = 1 if after.day > self.day else 0
            return after + relativedelta(day=self.day, months=months)

        if self.frequency == self.QUARTERLY:
            valid_quarter_days = (1, 15, 31, 32, 46, 62, 63, 77, 93)
            if self.day is None or self.day not in valid_quarter_days:
                raise ValueError(
                    "specify day as 1, 15, or 31 times month "
                    "1, 2, or 3 for quarterly frequency"
                )

            # Get the month of the quarter, e.g. 0, 1, 2 and current quarter
            m = valid_quarter_days.index(self.day) // 3
            q = (after.month - 1) // 3
            d = self.day - (m * 31)

            # See if the date is in the current quarter
            npdate = after + relativedelta(month=((q * 3) + m + 1), day=d)
            if npdate < after:
                npdate = after + relativedelta(month=(((q + 1) * 3) + m + 1), day=d)
            return npdate

        if self.frequency == self.YEARLY:
            if self.day is None or self.day > 366 or self.day < 1:
                raise ValueError("yearly frequency requires day of year in range 1-366")

            years = 1 if after.timetuple().tm_yday > self.day else 0
            return after + relativedelta(yearday=self.day, years=years)

        raise ValueError(
            "cannot compute next date for {} frequency after {}".format(
                self.get_frequency_display().lower(),
                after,
            ))

    def has_next_payment_date(self, after=None):
        """
        Returns True if a next payment date can be computed, otherwise returns False
        along with the exception that was raised. This method is used in validation and
        is a bit LBYL, but is intended to prevent 500 exceptions.
        """
        try:
            _ = self.next_payment_date(after=after)
            return True, None
        except ValueError as e:
            return False, str(e)

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
