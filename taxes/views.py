# taxes.views
# Tax views and controllers
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 16:36:54 2018 -0400
#
# ID: views.py [20315d2] benjamin@bengfort.com $

"""
Tax views and controllers
"""

##########################################################################
## Imports
##########################################################################

import csv

from .models import TaxReturn
from .serializers import TaxReturnSerializer

from django.http import HttpResponse
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets
from rest_framework import permissions


##########################################################################
## HTML Views
##########################################################################

class TaxesDashboard(LoginRequiredMixin, ListView):

    model = TaxReturn
    ordering = "-year"
    template_name = "taxes.html"
    context_object_name = "tax_returns"

    def get_context_data(self, **kwargs):
        context = super(TaxesDashboard, self).get_context_data(**kwargs)
        context['dashboard'] = 'taxes'

        return context


class TaxesCSVDownload(LoginRequiredMixin, ListView):

    model = TaxReturn
    ordering = "-year"
    context_object_name = "tax_returns"

    def render_to_response(self, context, **response_kwargs):
        """
        Generates a CSV file for download as an attachment
        """
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="tax_returns.csv"'

        writer = csv.writer(response)
        writer.writerow(["Year", "Income", "AGI", "Federal Taxes", "Local Taxes"])
        for irs in context[self.context_object_name]:
            writer.writerow([
                irs.year, irs.income, irs.agi, irs.federal_tax, irs.local_tax
            ])

        return response


##########################################################################
## API Views
##########################################################################

class TaxReturnViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = TaxReturn.objects.all()
    serializer_class = TaxReturnSerializer
    permission_classes = [permissions.IsAdminUser]
