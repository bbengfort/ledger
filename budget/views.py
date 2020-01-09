# budget.views
# Views for the budget app
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed May 01 21:26:07 2019 -0400
#
# Copyright (C) 2019 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: views.py [] benjamin@bengfort.com $

"""
Views for the budget app
"""

##########################################################################
## Imports
##########################################################################

from .models import Budget

from django.http import Http404
from django.utils.translation import gettext as _
from django.views.generic.base import RedirectView
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin


##########################################################################
## HTML Views
##########################################################################

class LatestBudget(LoginRequiredMixin, RedirectView):

    permanent = False
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        """
        Returns the latest budget by year, otherwise raises 404
        """
        try:
            latest = Budget.objects.latest()
        except Budget.DoesNotExist:
            raise Http404("No budgets have been created yet")

        return latest.get_absolute_url()


class BudgetDashboard(LoginRequiredMixin, DetailView):

    model = Budget
    template_name = "budget.html"
    context_object_name = "budget"

    def get_object(self, queryset=None):
        """
        Returns the associated budget by year.
        """
        if queryset is None:
            queryset = self.get_queryset()

        year = self.kwargs.get("year")

        if not year:
            raise AttributeError((
                "Generic detail view {} must be called with year in the URLconf"
            ).format(self.__class__.__name__))

        try:
            # Get the single item from the filtered queryset
            obj = queryset.prefetch_related().get(year=year)
        except queryset.model.DoesNotExist:
            verbose_name = queryset.model._meta.verbose_name
            raise Http404(_("No {} found matching the query").format(verbose_name))

        return obj

    def get_context_data(self, **kwargs):
        context = super(BudgetDashboard, self).get_context_data(**kwargs)
        context['dashboard'] = 'budget'
        return context


class BudgetArchives(LoginRequiredMixin, ListView):

    model = Budget
    template_name = "budget_archive.html"
    context_object_name = "budgets"

    def get_context_data(self, **kwargs):
        context = super(BudgetArchives, self).get_context_data(**kwargs)
        context['dashboard'] = 'budget'
        return context
