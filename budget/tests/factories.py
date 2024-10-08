# budget.tests.factories
# Factory Boy model factories for budget models.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu May 02 10:59:37 2019 -0400
#
# Copyright (C) 2019 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: factories.py [] benjamin@bengfort.com $

"""
Factory Boy model factories for budget models.
"""

##########################################################################
## Imports
##########################################################################

import factory
import factory.fuzzy
import factory.django

from budget.models import Budget, LineItem, Subscription


##########################################################################
## Budget and Line Item Factories
##########################################################################

class BudgetFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Budget

    year = 2002
    description = factory.Faker('text')


class LineItemFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = LineItem


class SubscriptionFactory(factory.django.DjangoModelFactory):

    name = factory.Faker('company')
    notes = factory.Faker('text')
    amount = 19.99
    frequency = 12
    active = True
    exclude = False
    opened_on = factory.Faker('date')
    closed_on = None
    order = None

    class Meta:
        model = Subscription
