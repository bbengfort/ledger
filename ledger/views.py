# ledger.views
# Default application views for the application
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 12:02:36 2018 -0400
#
# ID: views.py [36d8a34] benjamin@bengfort.com $

"""
Default application views for the application
"""

##########################################################################
## Imports
##########################################################################

import ledger

from datetime import datetime

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from taxes.models import TaxReturn
from accounts.models import BalanceSheet, CreditScore


##########################################################################
## Views
##########################################################################

class Overview(LoginRequiredMixin, TemplateView):

    template_name = "site/overview.html"

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context = self.get_latest_sheet_context(context)
        context['dashboard'] = 'overview'
        context['credit_score'] = CreditScore.objects.filter(preferred=True).latest()
        context['credit_score_history'] = CreditScore.objects.order_by("-date")[:4]
        context['tax_return'] = TaxReturn.objects.latest()
        return context

    def get_latest_sheet_context(self, context):
        sheet = BalanceSheet.objects.latest()
        context['latest_sheet'] = sheet

        prev_sheet = sheet.prev_sheet()
        if prev_sheet:
            # Compute monthly savings
            ccash = sheet.balances.cash_accounts().totals()['ending__sum']
            pcash = prev_sheet.balances.cash_accounts().totals()['ending__sum']
            context['monthly_savings'] = ccash - pcash

            # Compute investment increase
            cinvt = sheet.balances.investment_accounts().totals()['ending__sum']
            pinvt = prev_sheet.balances.investment_accounts().totals()['ending__sum']
            context['investment_increase'] = float(cinvt / pinvt) * 100 if pinvt != 0 else 0
        else:
            context['monthly_savings'] = 0
            context['investment_increase'] = 0

        return context

##########################################################################
## API Views
##########################################################################

class HeartbeatViewSet(viewsets.ViewSet):
    """
    Endpoint for heartbeat checking, includes status and version.
    """

    permission_classes = [AllowAny]

    def list(self, request):
        return Response({
            "status": "ok",
            "version": ledger.get_version(),
            "revision": ledger.get_revision(short=True),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        })


##########################################################################
## Error Views
##########################################################################

def server_error(request, **kwargs):
    return render(request, template_name='errors/500.html', status=500)


def not_found(request, exception, **kwargs):
    return render(request, template_name='errors/404.html', status=404)


def permission_denied(request, exception, **kwargs):
    return render(request, template_name='errors/403.html', status=403)


def bad_request(request, exception, **kwargs):
    return render(request, template_name='errors/400.html', status=400)
