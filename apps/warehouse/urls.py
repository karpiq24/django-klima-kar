from django.urls import path
from apps.warehouse import views

app_name = "warehouse"
urlpatterns = [
    path("towary", views.WareTableView.as_view(), name="wares"),
    path(
        "towary/remanent", views.ExportWareInventory.as_view(), name="wares_inventory"
    ),
    path("towary/nowy", views.WareCreateView.as_view(), name="ware_create"),
    path(
        "towary/<str:slug>,<int:pk>", views.WareDetailView.as_view(), name="ware_detail"
    ),
    path(
        "towary/<str:slug>,<int:pk>/edycja",
        views.WareUpdateView.as_view(),
        name="ware_update",
    ),
    path(
        "towary/create_ajax",
        views.WareCreateAjaxView.as_view(),
        name="ware_create_ajax",
    ),
    path("get_ware_data", views.GetWareData.as_view(), name="get_ware_data"),
    path(
        "ware_autocomplete", views.WareAutocomplete.as_view(), name="ware_autocomplete"
    ),
    path(
        "ware_autocomplete_create",
        views.WareAutocomplete.as_view(modal_create=True),
        name="ware_autocomplete_create",
    ),
    path(
        "ware_name_autocomplete",
        views.WareNameAutocomplete.as_view(),
        name="ware_name_autocomplete",
    ),
    path("faktury", views.InvoiceTableView.as_view(), name="invoices"),
    path("faktury/nowa", views.InvoiceCreateView.as_view(), name="invoice_create"),
    path(
        "faktury/<str:slug>,<int:pk>",
        views.InvoiceDetailView.as_view(),
        name="invoice_detail",
    ),
    path(
        "faktury/<str:slug>,<int:pk>/edycja",
        views.InvoiceUpdateView.as_view(),
        name="invoice_update",
    ),
    path("dostawcy", views.SupplierTableView.as_view(), name="suppliers"),
    path("dostawcy/nowy", views.SupplierCreateView.as_view(), name="supplier_create"),
    path(
        "dostawcy/<str:slug>,<int:pk>",
        views.SupplierDetailView.as_view(),
        name="supplier_detail",
    ),
    path(
        "dostawcy/<str:slug>,<int:pk>/edycja",
        views.SupplierUpdateView.as_view(),
        name="supplier_update",
    ),
    path(
        "supplier_autocomplete",
        views.SupplierAutocomplete.as_view(),
        name="supplier_autocomplete",
    ),
    path(
        "supplier_autocomplete_create",
        views.SupplierAutocomplete.as_view(create_field="name"),
        name="supplier_autocomplete_create",
    ),
    path(
        "scannded_to_invoice",
        views.ScannedToInvoiceView.as_view(),
        name="scannded_to_invoice",
    ),
]
