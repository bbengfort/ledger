# accounts.views.balance
# Balance sheet related views (HTML)
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed Oct 03 10:26:30 2018 -0400
#
# ID: balance.py [] benjamin@bengfort.com $

"""
Balance sheet related views (HTML)
"""

##########################################################################
## Imports
##########################################################################

from ..models import BalanceSheet
from ..models import Account, Payment

from django.http import Http404
from django.views.generic import DetailView
from django.utils.translation import gettext as _
from django.views.generic.dates import ArchiveIndexView
from django.contrib.auth.mixins import LoginRequiredMixin

from collections import defaultdict


__all__ = [
    "BalanceSheetArchives", "BalanceSheetView", "EditBalanceSheet",
]


##########################################################################
## Accounting HTML Views
##########################################################################

class BalanceSheetArchives(LoginRequiredMixin, ArchiveIndexView):

    model = BalanceSheet
    date_field = "date"
    make_object_list = True
    allow_future = True
    template_name = "balance_sheet_archive.html"
    context_object_name = "sheets"

    def get_context_data(self, **kwargs):
        context = super(BalanceSheetArchives, self).get_context_data(**kwargs)
        context['dashboard'] = 'sheets'

        # Create a hierarchical index of sheets
        context["years"] = {
            dt.year: context['sheets'].filter(date__year=dt.year)
            for dt in context['date_list']
        }

        return context


class BalanceSheetView(LoginRequiredMixin, DetailView):

    model = BalanceSheet
    template_name = "balance_sheet.html"
    print_template_name = "balance_sheet_print.html"
    context_object_name = "sheet"

    def get_object(self, queryset=None):
        """
        Returns the balance sheet by date.
        """
        if queryset is None:
            queryset = self.get_queryset()

        year = self.kwargs.get('year')
        month = self.kwargs.get('month')

        if not year or not month:
            raise AttributeError(
                "Generic detail view %s must be called with "
                "the year and month in the URLconf" % self.__class__.__name__
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get_month(year, month)
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_template_names(self):
        """
        Returns the print template name if print query, otherwise returns super.
        """
        if self.request.GET.get('print', False):
            return [self.print_template_name]
        return super(BalanceSheetView, self).get_template_names()

    def get_context_data(self, **kwargs):
        """
        Create the context data for the view
        """
        context = super(BalanceSheetView, self).get_context_data(**kwargs)
        context['dashboard'] = 'sheets'
        return context


class EditBalanceSheet(BalanceSheetView):

    model = BalanceSheet
    template_name = "balance_sheet_edit.html"

    def get_context_data(self, **kwargs):
        """
        Context data to populate form selections and other elements.
        """
        context = super(EditBalanceSheet, self).get_context_data(**kwargs)

        # Add hierarchical accounts for account selection
        context["accounts"] = defaultdict(list)
        accounts = Account.objects.filter(active=True).order_by("order")

        for account in accounts:
            context["accounts"][account.get_type_display()].append(account)

        # Add payments for payment selection
        context["payments"] = defaultdict(list)
        payments = Payment.objects.filter(active=True)

        for payment in payments:
            context["payments"][payment.get_frequency_display()].append(payment)

        # Django cannot parse defaultdict, so make sure to change factory before return
        context["accounts"].default_factory = None
        context["payments"].default_factory = None
        return context
