# accounts.tests.test_models.test_credit
# Test the credit score models
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Nov 01 10:32:42 2018 -0400
#
# ID: test_credit.py [] benjamin@bengfort.com $

"""
Test the credit score models
"""

##########################################################################
## Imports
##########################################################################

import pytest

from ..factories import *

# All tests in this module use the database
pytestmark = pytest.mark.django_db


##########################################################################
## Test Credit Score
##########################################################################

@pytest.mark.parametrize("score, description, percent", [
    (800, "Exceptional", 94.11764705882352),
    (760, "Very Good", 89.41176470588236),
    (710, "Good", 83.52941176470588),
    (623, "Fair", 73.29411764705883),
    (423, "Very Poor", 49.76470588235294),
])
def test_credit_score(score, description, percent):
    """
    Test credit score properties with a variety of scores
    """
    score = CreditScoreFactory(score=score)
    assert score.description == description
    assert score.percent == percent
