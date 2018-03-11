# flake8: noqa
from django.urls import path
from apps.warehouse import views

app_name = 'warehouse'
urlpatterns = [
    path('wares', views.WareTableView.as_view(), name='wares'),
    path('wares/export', views.WareTableView.as_view(), name='wares_export'),
    path('wares/create', views.WareCreateView.as_view(), name='ware_create'),
    path('wares/create_ajax', views.WareCreateAjaxView.as_view(), name='ware_create_ajax'),
    path('wares/<int:pk>', views.WareDetailView.as_view(), name='ware_detail'),
    path('wares/<int:pk>/update', views.WareUpdateView.as_view(), name='ware_update'),
    path('get_ware_data', views.GetWareData.as_view(), name='get_ware_data'),
    path('ware_autocomplete', views.WareAutocomplete.as_view(), name='ware_autocomplete'),
    path('ware_autocomplete_create', views.WareAutocomplete.as_view(modal_create=True), name='ware_autocomplete_create'),
    path('ware_name_autocomplete', views.WareNameAutocomplete.as_view(), name='ware_name_autocomplete'),

    path('invoices', views.InvoiceTableView.as_view(), name='invoices'),
    path('invoices/create', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/update', views.InvoiceUpdateView.as_view(), name='invoice_update'),

    path('suppliers', views.SupplierTableView.as_view(), name="suppliers"),
    path('suppliers/create', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/update', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('supplier_autocomplete', views.SupplierAutocomplete.as_view(), name='supplier_autocomplete'),
    path('supplier_autocomplete_create', views.SupplierAutocomplete.as_view(create_field='name'), name='supplier_autocomplete_create'),
]
