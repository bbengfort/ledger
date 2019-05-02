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

from budget.models import Budget, LineItem

##########################################################################
## Budget and Line Item Factories
##########################################################################

class BudgetFactory(factory.DjangoModelFactory):

    class Meta:
        model = Budget

    year = 2002
    description = factory.Faker('text')


class LineItemFactory(factory.DjangoModelFactory):

    class Meta:
        model = LineItem