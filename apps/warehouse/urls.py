from django.conf.urls import url
from apps.warehouse import views

app_name = 'warehouse'
urlpatterns = [
    url(r'^wares$', views.WareFilteredSingleTableView.as_view(), name="wares"),
    url(r'^invoices$', views.InvoiceFilteredSingleTableView.as_view(), name="invoices"),
    url(r'^suppliers$', views.SupplierFilteredSingleTableView.as_view(), name="suppliers"),
]
