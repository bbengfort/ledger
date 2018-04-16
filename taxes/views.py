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

from ledger import colors
from .models import TaxReturn

from collections import defaultdict

from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from bokeh.resources import CDN
from bokeh.plotting import figure
from bokeh.transform import dodge
from bokeh.embed import components
from bokeh.models import ColumnDataSource, NumeralTickFormatter


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

        # Create bokeh figure components
        context['bokeh'] = dict(
            zip(('script', 'div'), components(self.income_by_year(), CDN))
        )

        return context

    def income_by_year(self):
        # TODO: add via API
        data = defaultdict(list)

        for r in self.get_queryset().order_by('year'):
            data['years'].append(str(r.year))
            data['income'].append(r.income)
            data['agi'].append(r.agi)

        source = ColumnDataSource(data=data)

        # create a new plot with a title and axis labels
        plot = figure(
            title="Income by Year", plot_height=300, responsive=True,
            x_axis_label='Year', y_axis_label='USD ($)',
            x_range=data['years'], y_range=(0, 200000),
            tools="pan,box_zoom,save,reset"
        )

        # add a line renderer with legend and line thickness
        plot.vbar(
            x=dodge('years', -0.105, range=plot.x_range), top='income',
            legend="Income", color=colors.BLUE, width=0.2, source=source)

        plot.vbar(
            x=dodge('years', 0.105, range=plot.x_range), top='agi',
            legend="AGI", color=colors.GREEN, width=0.2, source=source)


        # set the final plot styles
        plot.yaxis.formatter=NumeralTickFormatter(format="0,0")
        plot.x_range.range_padding = 0.1
        plot.xgrid.grid_line_color = None
        plot.legend.location = "top_center"
        plot.legend.orientation = "horizontal"

        return plot


##########################################################################
## API Views
##########################################################################
