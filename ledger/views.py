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

from accounts.models import BalanceSheet, CreditScore


##########################################################################
## Views
##########################################################################

class Overview(LoginRequiredMixin, TemplateView):

    template_name = "site/overview.html"

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        context['dashboard'] = 'overview'
        context['latest_sheet'] = BalanceSheet.objects.latest()
        context['credit_score'] = CreditScore.objects.filter(preferred=True).latest()
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
