# flake8: noqa
from django.urls import path
from apps.stats import views

app_name = 'stats'
urlpatterns = [
    path('supplier_all_invoices_value', views.SupplierAllInvoicesValue.as_view(), name='supplier_all_invoices_value'),
    path('supplier_last_year_invoices_value', views.SupplierAllInvoicesValue.as_view(last_year=True), name='supplier_last_year_invoices_value'),
    path('ware_purchase_quantity', views.WarePurchaseQuantity.as_view(), name='ware_purchase_quantity'),
    path('ware_purchase_quantity_last_year', views.WarePurchaseQuantity.as_view(last_year=True), name='ware_purchase_quantity_last_year'),
    path('invoices_value_yearly', views.InvoicesValueYearly.as_view(), name='invoices_value_yearly'),
    path('invoices_value_monthly', views.InvoicesValueMonthly.as_view(), name='invoices_value_monthly'),
    path('ware_purchase_cost/<int:pk>', views.WarePurchaseCost.as_view(), name='ware_purchase_cost'),

    path('sale_invoices_value_monthly', views.SaleInvoicesValueMonthly.as_view(), name='sale_invoices_value_monthly'),
    path('sale_invoices_value_yearly', views.SaleInvoicesValueYearly.as_view(), name='sale_invoices_value_yearly'),
]
