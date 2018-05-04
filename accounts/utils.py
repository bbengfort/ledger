# utils
# Helpers and utilities for the accounts app
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu May 03 20:17:30 2018 -0400
#
# ID: utils.py [] benjamin@bengfort.com $

"""
Helpers and utilities for the accounts app
"""

##########################################################################
## Imports
##########################################################################

from enum import Enum


##########################################################################
## Currency
##########################################################################

class Currency(Enum):

    USD = "USD"
    GBP = "GBP"
    EUR = "EUR"
    CNY = "CNY"
    JPY = "JPY"
    MXN = "MXN"

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)

    @property
    def symbol(self):
        """
        Returns the currency symbol
        """
        return {
            "USD": "$",
            "GBP": "£",
            "EUR": "€",
            "CNY": "角",
            "JPY": "¥",
            "MXN": "$",
        }[self.value]
