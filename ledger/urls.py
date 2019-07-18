# ledger.urls
# Ledger URL configuration
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Sat Apr 14 10:20:15 2018 -0400
#
# ID: urls.py [36d8a34] benjamin@bengfort.com $

"""
Ledger URL configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

##########################################################################
## Imports
##########################################################################

from django.contrib import admin
from django.urls import path, include
from rest_framework_nested import routers

from ledger.views import *
from accounts.views import *
from budget.views import *
from taxes.views import *


##########################################################################
## Endpoint Discovery
##########################################################################

# Top level router
router = routers.DefaultRouter()
router.register(r'status', HeartbeatViewSet, "status")
router.register(r'sheets', BalanceSheetViewSet, "sheets")
router.register(r'accounts', AccountViewSet, "accounts")
router.register(r'payments', PaymentsAPIView, "payments")
router.register(r'returns', TaxReturnViewSet, "returns")
router.register(r'cashflow', CashFlow, "cashflow")

# Routes nested below sheets
sheets_router = routers.NestedDefaultRouter(router, r'sheets', lookup='sheet')
sheets_router.register(r'balances', BalanceViewSet, base_name='sheet-balances')
sheets_router.register(r'transactions', TransactionViewSet, base_name='sheet-transactions')


##########################################################################
## URL Patterns
##########################################################################

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),

    # Application URLs
    path('', Overview.as_view(), name="overview"),
    path('taxes/', TaxesDashboard.as_view(), name="taxes"),
    path('budget/', LatestBudget.as_view(), name="budget"),
    path('budget/<int:year>/', BudgetDashboard.as_view(), name="budget-detail"),
    path('sheets/', BalanceSheetArchives.as_view(), name="sheets-archive"),
    path('sheets/<int:year>-<int:month>/', BalanceSheetView.as_view(), name="sheets-detail"),
    path('sheets/<int:year>-<int:month>/edit/', EditBalanceSheet.as_view(), name="sheets-edit"),

    # Authentication URLs
    path('user/', include(('social_django.urls', 'social_django'), namespace='social')),
    path('user/', include('django.contrib.auth.urls')),

    ## REST API Urls
    path('api/', include((router.urls, 'rest_framework'), namespace="api")),
    path('api/', include((sheets_router.urls, 'rest_framework'), namespace="sheets-api")),
]

##########################################################################
## Error handling
##########################################################################

# Do not import anything for the handler404,
# or whatnot from the django.conf.urls

handler400 = 'ledger.views.bad_request'
handler403 = 'ledger.views.permission_denied'
handler404 = 'ledger.views.not_found'
handler500 = 'ledger.views.server_error'
