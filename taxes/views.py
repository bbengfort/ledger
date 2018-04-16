# taxes.views
# Tax views and controllers
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 16:36:54 2018 -0400
#
# ID: views.py [] benjamin@bengfort.com $

"""
Tax views and controllers
"""

##########################################################################
## Imports
##########################################################################

from .models import TaxReturn

from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


##########################################################################
## HTML Views
##########################################################################

class TaxesDashboard(ListView, LoginRequiredMixin):

    model = TaxReturn
    ordering = "-year"
    template_name = "taxes.html"
    context_object_name = "tax_returns"

    def get_context_data(self, **kwargs):
        context = super(TaxesDashboard, self).get_context_data(**kwargs)
        context['dashboard'] = 'taxes'
        return context


##########################################################################
## API Views
##########################################################################
