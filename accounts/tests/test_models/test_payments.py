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

from accounts.models import Payment
from ..factories import PaymentFactory

# All tests in this module use the database
pytestmark = pytest.mark.django_db


##########################################################################
## Payment Tests
##########################################################################

class TestPayment(object):
    """
    Test the Payments model
    """

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

        regex = re.compile(r'([$£€角¥])([\d\.]+) (\w+) payments from ([\w\s]+) to ([\w\s]+)', re.I)
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