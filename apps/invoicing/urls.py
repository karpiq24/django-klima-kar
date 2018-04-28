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
    path('sale_invoices/<int:pk>/print_pdf', views.SaleInvoicePDFView.as_view(print_version=True), name='sale_invoice_print_pdf'),
    path('export_refrigerant_weights', views.ExportRefrigerantWeights.as_view(), name='export_refrigerant_weights'),
    path('sale_invoice_email', views.SendEmailView.as_view(), name='sale_invoice_email'),

    path('services', views.ServiceTemplateTableView.as_view(), name='service_templates'),
    path('services/<int:pk>', views.ServiceTemplateDetailView.as_view(), name='service_template_detail'),
    path('services/<int:pk>/update', views.ServiceTemplateUpdateView.as_view(), name='service_template_update'),
    path('services/create', views.ServiceTemplateCreateView.as_view(), name='service_template_create'),
    path('service_autocomplete', views.ServiceTemplateAutocomplete.as_view(), name='service_template_autocomplete'),
    path('get_service_data', views.ServiceTemplateGetDataView.as_view(), name='get_service_template'),
    
    path('contractors', views.ContractorTableView.as_view(), name='contractors'),
    path('contractors/<int:pk>', views.ContractorDetailView.as_view(), name='contractor_detail'),
    path('contractors/<int:pk>/update', views.ContractorUpdateView.as_view(), name='contractor_update'),
    path('contractors/<int:pk>/update_ajax', views.ContractorUpdateAjaxView.as_view(), name='contractor_update_ajax'),
    path('contractors/create', views.ContractorCreateView.as_view(), name='contractor_create'),
    path('contractors/create_ajax', views.ContractorCreateAjaxView.as_view(), name='contractor_create_ajax'),
    path('contractor_gus', views.ContractorGUS.as_view(), name='contractor_gus'),
    path('contractor_autocomplete', views.ContractorAutocomplete.as_view(), name='contractor_autocomplete'),
    path('contractor_autocomplete_create', views.ContractorAutocomplete.as_view(modal_create=True), name='contractor_autocomplete_create'),
    path('get_contractor_data', views.ContractorGetDataView.as_view(), name='get_contractor'),
]
