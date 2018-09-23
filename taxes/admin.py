# taxes.admin
# Tax admin configuration
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 16:36:54 2018 -0400
#
# ID: admin.py [20315d2] benjamin@bengfort.com $

"""
Tax admin configuration
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin
from .models import TaxReturn

# Register your models here.
admin.site.register(TaxReturn)
