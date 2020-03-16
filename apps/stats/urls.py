# flake8: noqa
from django.urls import path
from apps.stats import views

app_name = "stats"
urlpatterns = [
    path("metrics", views.Metrics.as_view(), name="metrics"),
    path("summary", views.GetSummary.as_view(), name="summary"),
    path(
        "purchase_invoices_history",
        views.PurchaseInvoicesHistory.as_view(),
        name="purchase_invoices_history",
    ),
    path(
        "purchase_invoices_history/<int:supplier>",
        views.PurchaseInvoicesHistory.as_view(),
        name="purchase_invoices_history_per_supplier",
    ),
    path(
        "supplier_purchase_history",
        views.SupplierPurchaseHistory.as_view(),
        name="supplier_purchase_history",
    ),
    path(
        "ware_purchase_history",
        views.WarePurchaseHistory.as_view(),
        name="ware_purchase_history",
    ),
    path(
        "ware_purchase_cost/<int:pk>",
        views.WarePurchaseCost.as_view(),
        name="ware_purchase_cost",
    ),
    path(
        "ware_price_changes",
        views.WarePriceChanges.as_view(),
        name="ware_price_changes",
    ),
    path(
        "sale_invoices_history",
        views.SaleInvoicesHistory.as_view(),
        name="sale_invoices_history",
    ),
    path("due_payments", views.DuePayments.as_view(), name="due_payments"),
    path(
        "refrigerant_history",
        views.RefrigerantWeightsHistory.as_view(),
        name="refrigerant_history",
    ),
    path(
        "commission_history",
        views.CommissionHistory.as_view(),
        name="commission_history",
    ),
    path("ptu_list", views.PTUList.as_view(), name="ptu_list"),
    path("ptu_value", views.GetPTUValue.as_view(), name="ptu_value"),
    path("save_ptu", views.SavePTU.as_view(), name="save_ptu"),
]
