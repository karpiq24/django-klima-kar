# flake8: noqa
from django.urls import path
from apps.stats import views

app_name = 'stats'
urlpatterns = [
    path('supplier_all_invoices_value', views.SupplierAllInvoicesValue.as_view(), name='supplier_all_invoices_value'),
    path('ware_purchase_quantity', views.WarePurchaseQuantity.as_view(), name='ware_purchase_quantity'),
    path('invoices_value_yearly', views.InvoicesValueYearly.as_view(), name='invoices_value_yearly'),
    path('invoices_value_monthly', views.InvoicesValueMonthly.as_view(), name='invoices_value_monthly'),
]
