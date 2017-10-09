from django.conf.urls import url
from apps.warehouse import views

app_name = 'warehouse'
urlpatterns = [
    url(r'^wares$', views.WareTableView.as_view(), name='wares'),
    url(r'^wares/create$', views.WareCreateView.as_view(), name='ware_create'),
    url(r'^wares/(?P<pk>[-\w]+)/detail$', views.WareDetailView.as_view(), name='ware_detail'),
    url(r'^wares/(?P<pk>[-\w]+)/update$', views.WareUpdateView.as_view(), name='ware_update'),
    url(r'^get_ware_data$', views.GetWareData.as_view(), name='get_ware_data'),
    url(r'^ware_autocomplete$', views.WareAutocomplete.as_view(), name='ware_autocomplete'),
    url(r'^ware_name_autocomplete$', views.WareNameAutocomplete.as_view(), name='ware_name_autocomplete'),


    url(r'^invoices$', views.InvoiceTableView.as_view(), name='invoices'),
    url(r'^invoices/create$', views.InvoiceCreateView.as_view(), name='invoice_create'),
    url(r'^invoices/(?P<pk>[-\w]+)/detail$', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    url(r'^invoices/(?P<pk>[-\w]+)/update$', views.InvoiceUpdateView.as_view(), name='invoice_update'),

    url(r'^suppliers$', views.SupplierTableView.as_view(), name="suppliers"),
    url(r'^suppliers/create$', views.SupplierCreateView.as_view(), name='supplier_create'),
    url(r'^suppliers/(?P<pk>[-\w]+)/detail$', views.SupplierDetailView.as_view(), name='supplier_detail'),
    url(r'^suppliers/(?P<pk>[-\w]+)/update$', views.SupplierUpdateView.as_view(), name='supplier_update'),
    url(r'^supplier_autocomplete$', views.SupplierAutocomplete.as_view(), name='supplier_autocomplete'),
]
