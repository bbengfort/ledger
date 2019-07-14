# accounts.tests.test_views.test_api
# Tests for the API views in the accounts app.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Jul 07 23:04:09 2019 -0500
#
# Copyright (C) 2019 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: test_api.py [] benjamin@bengfort.com $

"""
Tests for the API views in the accounts app.
"""

##########################################################################
## Imports
##########################################################################

import pytest

from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from ..factories import TransactionFactory
from ..factories import AdminUserFactory, PaymentFactory

# All tests in this module use the database
pytestmark = pytest.mark.django_db


@pytest.fixture()
def admin_client(db):
    admin = AdminUserFactory.create()
    client = APIClient()
    assert client.login(username=admin.username, password=admin.password)
    return client


##########################################################################
## Test Payments API View
####################################################d######################

class TestPaymentsAPIView(object):

    def test_login_required(self, admin_client):
        """
        Assert that a login is required to access payments API
        """
        url = reverse("api:payments-list")

        # Admin client should already be logged in
        rep = admin_client.get(url)
        assert rep.status_code == 200

        # Logout admin client and try again
        admin_client.logout()
        rep = admin_client.get(url)
        assert rep.status_code == 403

    def test_actions(self, admin_client):
        """
        Ensure the endpoint is RESTful for payments
        """
        url = reverse("api:payments-list")
        rep = admin_client.options(url)
        assert rep.status_code == 200

        assert rep.get('Allow') == 'GET, POST, HEAD, OPTIONS'

        payment = PaymentFactory.create()
        rep = admin_client.options(payment.get_api_url())

        assert rep.get('Allow') == 'GET, PUT, PATCH, DELETE, HEAD, OPTIONS'

    def test_list(self, admin_client):
        """
        Test GET payments list
        """
        url = reverse("api:payments-list")
        rep = admin_client.get(url)
        assert len(rep.json()) == 0

        PaymentFactory.create()
        PaymentFactory.create()

        rep = admin_client.get(url)
        assert len(rep.json()) == 2

    def test_make_transaction(self, admin_client):
        """
        Test make transaction from payment detail action
        """
        payment = PaymentFactory.create()
        rep = admin_client.get(payment.get_api_url(action='transaction'))
        data = rep.json()

        # Get the account pk from the url (will be used as relation in API)
        for account in ('credit', 'debit'):
            url = data.pop(account)['url']
            pk = int(list(filter(None, url.split("/")))[-1])
            data[account+"_id"] = pk

        # Should be able to make a transactions from the response
        TransactionFactory.create(**data)
