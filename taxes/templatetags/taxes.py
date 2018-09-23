# taxes.templatetags.taxes
# Template helpers for the taxes app.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Apr 16 13:14:33 2018 -0400
#
# ID: taxes.py [0338d7a] benjamin@bengfort.com $

"""
Template helpers for the taxes app.
"""

##########################################################################
## Imports
##########################################################################

from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.simple_tag()
def prev_year_change(txr, field):
    if txr.prev_year_change(field) >= 0:
        icon = '<big><i class="fa fa-caret-up text-success"></i></big>'
    else:
        icon = '<big><i class="fa fa-caret-down text-danger"></i></big>'

    return mark_safe(icon)
