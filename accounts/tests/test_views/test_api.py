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

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from datetime import timedelta
from ..factories import this_month
from ..factories import BalanceSheetFactory, TransactionFactory
from ..factories import AdminUserFactory, UserFactory, PaymentFactory

from accounts.models import BalanceSheet


# All tests in this module use the database
pytestmark = pytest.mark.django_db


@pytest.fixture()
def admin_client(db):
    admin = AdminUserFactory.create()
    client = APIClient()
    assert client.login(username=admin.username, password=admin.password)
    return client


@pytest.fixture()
def client(db):
    user = UserFactory.create()
    client = APIClient()
    assert client.login(username=user.username, password=user.password)
    return client


##########################################################################
## Test API Authentication
##########################################################################

@pytest.mark.parametrize("endpoint", [
    "api:accounts-list", "api:sheets-list", "api:payments-list",
    "api:returns-list", "api:cashflow-list",
])
def test_require_authentication(endpoint, admin_client):
    url = reverse(endpoint)

    # Admin client should already be logged in
    rep = admin_client.get(url)
    assert rep.status_code == status.HTTP_200_OK, "didn't allow admin user access"

    # Logout admin client and try again
    admin_client.logout()
    rep = admin_client.get(url)
    assert rep.status_code == status.HTTP_403_FORBIDDEN, "allowed public access"


##########################################################################
## Test BalanceSheet ViewSet
##########################################################################

class TestBalanceSheetViewSet(object):

    def test_sheets_list(self, admin_client):
        url = reverse("api:sheets-list")

        rep = admin_client.get(url)
        assert rep.status_code == status.HTTP_200_OK
        assert len(rep.json()) == 0

        BalanceSheetFactory.create()
        BalanceSheetFactory.create(date=this_month() - timedelta(weeks=4))

        rep = admin_client.get(url)
        assert rep.status_code == status.HTTP_200_OK
        assert len(rep.json()) == 2

    def test_sheets_create(self, admin_client):
        url = reverse("api:sheets-list")
        assert BalanceSheet.objects.count() == 0

        data = {'date': '2019-10-01', 'memo': 'test balancesheet', 'title': 'Test BS'}
        rep = admin_client.post(url, data, format='json')
        assert rep.status_code == status.HTTP_201_CREATED
        assert BalanceSheet.objects.count() == 1

        for key, val in rep.json().items():
            if key in data:
                assert data[key] == val

    def test_sheets_create_only_date_required(self, admin_client):
        """
        Test date only post to sheets create endpoint (most common usage)
        """
        url = reverse("api:sheets-list")
        rep = admin_client.post(url, {'date': '2019-10-01'}, format='json')
        assert rep.status_code == status.HTTP_201_CREATED

        data = rep.json()
        assert data["date"] == '2019-10-01'
        assert data["memo"] is None
        assert data["title"] is not None
        assert data["title"] != ""

    def test_sheets_create_only_one_per_month(self, admin_client):
        """
        Ensure two sheets cannot be created for the same month
        """
        url = reverse("api:sheets-list")
        data = {'date': '2019-10-01'}

        # first post should be successful
        rep = admin_client.post(url, data, format='json')
        assert rep.status_code == status.HTTP_201_CREATED

        # second post should fail
        rep = admin_client.post(url, data, format='json')
        assert rep.status_code == status.HTTP_400_BAD_REQUEST

        # even with a different day it should fail
        rep = admin_client.post(url, {'date': '2019-10-15'}, format='json')
        assert rep.status_code == status.HTTP_400_BAD_REQUEST

        # delete should work
        detail_url = reverse("api:sheets-detail", kwargs={'date': '2019-10-01'})
        rep = admin_client.delete(detail_url)
        assert rep.status_code == status.HTTP_204_NO_CONTENT

        # post should be successful after delete
        rep = admin_client.post(url, data, format='json')
        assert rep.status_code == status.HTTP_201_CREATED

        # second post should fail
        rep = admin_client.post(url, data, format='json')
        assert rep.status_code == status.HTTP_400_BAD_REQUEST

    def test_sheets_detail(self, admin_client, balance_sheet):
        url = balance_sheet.get_api_url()

        rep = admin_client.get(url)
        assert rep.status_code == status.HTTP_200_OK

        data = rep.json()
        assert data["date"] == balance_sheet.date.strftime("%Y-%m-%d")
        assert data["title"] == balance_sheet.title
        assert data["memo"] == balance_sheet.memo
        assert len(data["balances"]) == balance_sheet.balances.count()
        assert len(data["transactions"]) == balance_sheet.transactions.count()

    def test_sheets_update_date(self, admin_client, balance_sheet):
        url = balance_sheet.get_api_url()
        data = {
            "date": balance_sheet.date + timedelta(days=2),
            "title": balance_sheet.title, "memo": balance_sheet.memo
        }

        rep = admin_client.put(url, data, format='json')
        assert rep.status_code == status.HTTP_200_OK

    def test_sheets_update_only_one_per_month(self, admin_client, balance_sheet):
        # Create the first balance sheet
        url = reverse("api:sheets-list")
        data = {'date': '2019-10-01', "title": "", "memo": ""}
        rep = admin_client.post(url, data, format='json')
        assert rep.status_code == status.HTTP_201_CREATED

        # Attempt to update the balance sheet to the non uniuqe month
        url = balance_sheet.get_api_url()
        data["title"] = balance_sheet.title
        data["memo"] = balance_sheet.memo
        rep = admin_client.put(url, data, format='json')
        assert rep.status_code == status.HTTP_400_BAD_REQUEST


##########################################################################
## Test Payments API View
####################################################d######################

class TestPaymentsAPIView(object):

    def test_actions(self, admin_client):
        """
        Ensure the endpoint is RESTful for payments
        """
        url = reverse("api:payments-list")
        rep = admin_client.options(url)
        assert rep.status_code == status.HTTP_200_OK

        assert rep.get('Allow') == 'GET, POST, HEAD, OPTIONS'

        payment = PaymentFactory.create()
        rep = admin_client.options(payment.get_api_url())
        assert rep.status_code == status.HTTP_200_OK

        assert rep.get('Allow') == 'GET, PUT, PATCH, DELETE, HEAD, OPTIONS'

    def test_list(self, admin_client):
        """
        Test GET payments list
        """
        url = reverse("api:payments-list")
        rep = admin_client.get(url)
        assert rep.status_code == status.HTTP_200_OK
        assert len(rep.json()) == 0

        PaymentFactory.create()
        PaymentFactory.create()

        rep = admin_client.get(url)
        assert rep.status_code == status.HTTP_200_OK
        assert len(rep.json()) == 2

    def test_make_transaction(self, admin_client):
        """
        Test make transaction from payment detail action
        """
        payment = PaymentFactory.create()
        rep = admin_client.get(payment.get_api_url(action='transaction'))
        assert rep.status_code == status.HTTP_200_OK

        data = rep.json()

        # Get the account pk from the url (will be used as relation in API)
        for account in ('credit', 'debit'):
            url = data.pop(account)['url']
            pk = int(list(filter(None, url.split("/")))[-1])
            data[account + "_id"] = pk

        # Should be able to make a transactions from the response
        TransactionFactory.create(**data)


##########################################################################
## Test Status Endpoint
##########################################################################

def test_status_no_auth(client):
    # Ensure client is logged out
    client.logout()

    url = reverse("api:status-list")
    rep = client.get(url)
    assert rep.status_code == status.HTTP_200_OK

    data = rep.json()
    assert "status" in data and data["status"] == "ok"
    assert "version" in data
    assert "revision" in data
    assert "timestamp" in data


def test_status_auth(client, admin_client):
    url = reverse("api:status-list")

    # Non Admin Users
    rep = client.get(url)
    assert rep.status_code == status.HTTP_200_OK

    # Admin Users
    rep = client.get(url)
    assert rep.status_code == status.HTTP_200_OK
