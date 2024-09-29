# budget.admin
# budget admin configuration
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed May 01 21:24:36 2019 -0400
#
# Copyright (C) 2019 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: admin.py [] benjamin@bengfort.com $

"""
budget admin configuration
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin
from .models import Budget, LineItem, Subscription, Category


class LineItemInline(admin.TabularInline):

    extra = 3
    model = LineItem

    def get_extra(self, request, obj=None, **kwargs):
        """
        Don't add any extra forms if the related object already exists.
        """
        if obj is not None and obj.line_items.count() > 0:
            return 0
        return self.extra


class BudgetAdmin(admin.ModelAdmin):

    inlines = [
        LineItemInline
    ]


# Register your models here.
admin.site.register(Budget, BudgetAdmin)
admin.site.register(Subscription)
admin.site.register(Category)
