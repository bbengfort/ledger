# taxes.serializers
# API serializers for taxes models
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed Oct 03 12:06:14 2018 -0400
#
# ID: serializers.py [] benjamin@bengfort.com $

"""
API serializers for taxes models
"""

##########################################################################
## Imports
##########################################################################

from .models import TaxReturn

from rest_framework import serializers


##########################################################################
## Model Serializers
##########################################################################

class TaxReturnSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = TaxReturn
        fields = "__all__"
        extra_kwargs = {
            "url": {"view_name": "api:returns-detail"}
        }
