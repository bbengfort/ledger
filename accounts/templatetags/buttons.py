# accounts.templatetags.buttons
# Quick buttons for accounting related actions
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jul 01 09:41:07 2019 -0400
#
# ID: buttons.py [] benjamin@bengfort.com $

"""
Quick buttons for accounting related actions
"""

##########################################################################
## Imports
##########################################################################

from django import template

# Register template tags
register = template.Library()


@register.inclusion_tag("components/buttons/print.html")
def print_button(icon_only=True, text="Print"):
    return {"text": text, "icon_only": icon_only}


@register.inclusion_tag("components/buttons/edit.html")
def edit_button(icon_only=True, text="Edit"):
    return {"text": text, "icon_only": icon_only}
