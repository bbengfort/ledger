# accounts.views
# Views and controllers for the account app.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed May 02 15:42:02 2018 -0400
#
# ID: views.py [] benjamin@bengfort.com $

"""
Views and controllers for the account app.
"""

##########################################################################
## Imports
##########################################################################

from datetime import date

from .models import BalanceSheet

from django.http import Http404
from django.views.generic import DetailView
from django.utils.translation import gettext as _
from django.views.generic.dates import ArchiveIndexView


##########################################################################
## Accounting HTML Views
##########################################################################

class BalanceSheetArchives(ArchiveIndexView):

    model = BalanceSheet
    date_field = "date"
    make_object_list = True
    allow_future = False
    template_name = "balance_sheet_archive.html"
    context_object_name = "sheets"

    def get_context_data(self, **kwargs):
        context = super(BalanceSheetArchives, self).get_context_data(**kwargs)
        context['dashboard'] = 'sheets'
        return context


class BalanceSheetView(DetailView):

    model = BalanceSheet
    template_name = "balance_sheet.html"
    context_object_name = "sheet"

    def get_object(self, queryset=None):
        """
        Returns the balance sheet by date.
        """
        if queryset is None:
            queryset = self.get_queryset()

        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')

        if not year or not month or not day:
            raise AttributeError(
                "Generic detail view %s must be called with the year, month "
                "and day in the URLconf." % self.__class__.__name__
            )

        queryset = queryset.filter(date=date(year, month, day))

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


    def get_context_data(self, **kwargs):
        context = super(BalanceSheetView, self).get_context_data(**kwargs)
        context['dashboard'] = 'sheets'
        return context
