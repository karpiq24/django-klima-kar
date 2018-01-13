# flake8: noqa
from django.urls import path
from apps.stats import views

app_name = 'stats'
urlpatterns = [
    path('supplier_all_invoices_value', views.SupplierAllInvoicesValue.as_view(), name='supplier_all_invoices_value'),
    path('invoices_value_all', views.InvoicesValueOverTime.as_view(), name='invoices_value_all'),
    path('invoices_value_last_year', views.InvoicesValueOverTime.as_view(last_year=True), name='invoices_value_last_year'),
    path('ware_purchase_quantity', views.WarePurchaseQuantity.as_view(), name='ware_purchase_quantity'),
]
