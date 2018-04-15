# flake8: noqa
from django.urls import path
from apps.stats import views

app_name = 'stats'
urlpatterns = [
    path('purchase_invoices_history', views.PurchaseInvoicesHistory.as_view(), name='purchase_invoices_history'),
    path('supplier_purchase_history', views.SupplierPurchaseHistory.as_view(), name='supplier_purchase_history'),
    path('ware_purchase_history', views.WarePurchaseHistory.as_view(), name='ware_purchase_history'),
    path('ware_purchase_cost/<int:pk>', views.WarePurchaseCost.as_view(), name='ware_purchase_cost'),

    path('sale_invoices_history', views.SaleInvoicesHistory.as_view(), name='sale_invoices_history'),
    path('refrigerant_history', views.RefrigerantWeightsHistory.as_view(), name='refrigerant_history'),
]
