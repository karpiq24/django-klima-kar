# flake8: noqa
from django.urls import path
from apps.invoicing import views

app_name = 'invoicing'
urlpatterns = [
    path('sale_invoices', views.SaleInvoiceTableView.as_view(), name='sale_invoices'),
    path('sale_invoices/<int:pk>', views.SaleInvoiceDetailView.as_view(), name='sale_invoice_detail'),
    path('sale_invoices/create/<type>', views.SaleInvoiceCreateView.as_view(), name='sale_invoice_create'),
    path('sale_invoices/<int:pk>/update', views.SaleInvoiceUpdateView.as_view(), name='sale_invoice_update'),
    path('sale_invoices/<int:pk>/pdf', views.SaleInvoicePDFView.as_view(), name='sale_invoice_pdf'),
    
    path('contractors', views.ContractorTableView.as_view(), name='contractors'),
    path('contractors/<int:pk>', views.ContractorDetailView.as_view(), name='contractor_detail'),
    path('contractors/<int:pk>/update', views.ContractorUpdateView.as_view(), name='contractor_update'),
    path('contractors/create', views.ContractorCreateView.as_view(), name='contractor_create'),
    path('contractors/create_ajax', views.ContractorCreateAjaxView.as_view(), name='contractor_create_ajax'),
    path('contractor_gus', views.ContractorGUS.as_view(), name='contractor_gus'),
    path('contractor_autocomplete', views.ContractorAutocomplete.as_view(), name='contractor_autocomplete'),
    path('contractor_autocomplete_create', views.ContractorAutocomplete.as_view(modal_create=True), name='contractor_autocomplete_create'),
]
