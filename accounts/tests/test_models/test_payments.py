# accounts.tests.test_models.test_payments
# Tests for payments models
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jun 24 10:45:28 2019 -0400
#
# ID: test_payments.py [] benjamin@bengfort.com $

"""
Tests for payments models
"""

##########################################################################
## Imports
##########################################################################

import re
import pytest

from datetime import date, timedelta

from accounts.models import Payment
from ..factories import PaymentFactory
from ..factories import BillingAccountFactory, TransactionFactory

# All tests in this module use the database
pytestmark = pytest.mark.django_db


##########################################################################
## Payment Tests
##########################################################################

class TestPayment(object):
    """
    Test the Payments model
    """

    def test_get_api_url(self):
        """
        Test get_api_url works as expectd with action
        """
        payment = PaymentFactory.build(id=42)
        assert payment.get_api_url() == "/api/payments/42/"
        assert payment.get_api_url(action="transaction") == "/api/payments/42/transaction/"

        with pytest.raises(ValueError, match="unknown API action"):
            payment.get_api_url(action="foo")

    def test_transactions(self):
        """
        Test that payment transactions are returned correctly
        """
        # Create the payment
        payment = PaymentFactory.create(
            description="test payment",
            frequency=Payment.MONTHLY
        )

        # Get the associated accounts and create an alternate
        bank = payment.credit
        electric = payment.debit
        water = BillingAccountFactory.create(name="Water Bill")

        # Make a bunch of transactions
        t1 = TransactionFactory.create(credit=bank, debit=electric)
        t2 = TransactionFactory.create(credit=bank, debit=water)

        assert payment.transactions().count() == 1
        assert t1 in payment.transactions()
        assert t2 not in payment.transactions()

    @pytest.mark.parametrize("frequency,after,day,expected", [
        (Payment.DAILY, "2019-07-01", None, date(2019, 7, 2)),
        (Payment.WEEKLY, "2019-07-01", 4, date(2019, 7, 5)),
        (Payment.WEEKLY, "2019-07-05", 4, date(2019, 7, 12)),
        (Payment.WEEKLY, "2019-07-06", 4, date(2019, 7, 12)),
        (Payment.MONTHLY, "2019-06-26", 31, date(2019, 6, 30)),
        (Payment.MONTHLY, "2019-07-01", 15, date(2019, 7, 15)),
        (Payment.MONTHLY, "2019-07-26", 15, date(2019, 8, 15)),
        (Payment.MONTHLY, "2019-07-01", 31, date(2019, 7, 31)),
        (Payment.MONTHLY, "2019-02-01", 31, date(2019, 2, 28)),
        (Payment.QUARTERLY, "2019-05-01", 1, date(2019, 7, 1)),
        (Payment.QUARTERLY, "2019-05-01", 15, date(2019, 7, 15)),
        (Payment.QUARTERLY, "2019-05-01", 31, date(2019, 7, 31)),
        (Payment.QUARTERLY, "2019-05-01", 32, date(2019, 5, 1)),
        (Payment.QUARTERLY, "2019-05-01", 46, date(2019, 5, 15)),
        (Payment.QUARTERLY, "2019-05-01", 62, date(2019, 5, 31)),
        (Payment.QUARTERLY, "2019-05-01", 63, date(2019, 6, 1)),
        (Payment.QUARTERLY, "2019-05-01", 77, date(2019, 6, 15)),
        (Payment.QUARTERLY, "2019-05-01", 93, date(2019, 6, 30)),
        (Payment.YEARLY, "2019-07-01", 105, date(2020, 4, 14)),  # 2020 is a leap year
        (Payment.YEARLY, "2019-07-01", 294, date(2019, 10, 21)),
    ])
    def test_next_payment_date(self, frequency, after, day, expected):
        """
        Tests the next payment date after July 1, 2019 based on frequency
        """
        payment = PaymentFactory.build(frequency=frequency, day=day)
        assert payment.next_payment_date(after=after) == expected
        assert payment.has_next_payment_date() == (True, None)

    def test_next_payment_date_today(self):
        """
        Test that next payment date defaults to today
        """
        payment = PaymentFactory.build(frequency=Payment.DAILY)
        assert payment.next_payment_date() == date.today() + timedelta(days=1)
        assert payment.has_next_payment_date() == (True, None)

    @pytest.mark.parametrize("frequency,day,error", [
        (Payment.INFREQUENT, None, "cannot compute next date for infrequent"),
        (Payment.WEEKLY, None, "weekly frequency requires day of week in range 0-6"),
        (Payment.WEEKLY, 7, "weekly frequency requires day of week in range 0-6"),
        (Payment.MONTHLY, None, "monthly frequency requires day of month in range 1-31"),
        (Payment.MONTHLY, 0, "monthly frequency requires day of month in range 1-31"),
        (Payment.MONTHLY, 32, "monthly frequency requires day of month in range 1-31"),
        (Payment.QUARTERLY, 48, "specify day as 1, 15, or 31 times month 1, 2, or 3 for quarterly frequency"),
        (Payment.YEARLY, 0, "yearly frequency requires day of year in range 1-366"),
        (Payment.YEARLY, 367, "yearly frequency requires day of year in range 1-366"),
    ])
    def test_next_payment_date_exceptions(self, frequency, day, error):
        """
        Assert that infrequent payments cannot compute next payment date
        """
        with pytest.raises(ValueError, match=error):
            payment = PaymentFactory.build(frequency=frequency, day=day)
            payment.next_payment_date()
            assert payment.has_next_payment_date() == (False, ValueError(error))

    def test_str_method(self):
        """
        Test the string representation of the payment
        """
        # Default build of the payment with a description
        payment = PaymentFactory.build(
            description="test payment",
            frequency=Payment.MONTHLY
        )

        # Description should always be used if it exists
        assert str(payment) == payment.description

        # Check frequency with an amount set
        payment.description = None
        assert payment.amount > 0.0

        regex = re.compile(
            r'([$£€角¥])([\d\.]+) (\w+) payments from ([\w\s]+) to ([\w\s]+)', re.I
        )
        match = regex.match(str(payment))
        assert match is not None, "could not match freq/amount payment string"
        assert match.groups()[1] == str(payment.amount)
        assert match.groups()[2].lower() == payment.get_frequency_display().lower()

        # Check frequency without an amount
        payment.amount = None
        regex = re.compile(r'(\w+) payments from ([\w\s]+) to ([\w\s]+)', re.I)
        match = regex.match(str(payment))
        assert match is not None, "could not match frequency w/o amount payment string"

        # Check no frequency
        payment.frequency = Payment.INFREQUENT
        regex = re.compile(r'Payments from ([\w\s]+) to ([\w\s]+)', re.I)
        match = regex.match(str(payment))
        assert match is not None, "could not match default payment string"
