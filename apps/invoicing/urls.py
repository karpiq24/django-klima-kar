# flake8: noqa
from django.urls import path
from apps.invoicing import views

app_name = 'invoicing'
urlpatterns = [
    path('faktury', views.SaleInvoiceTableView.as_view(), name='sale_invoices'),
    path('faktury/<str:kind>,<str:number>,<int:pk>', views.SaleInvoiceDetailView.as_view(), name='sale_invoice_detail'),
    path('faktury/nowa/<str:kind>,<type>', views.SaleInvoiceCreateView.as_view(), name='sale_invoice_create'),
    path('faktury/nowa/<str:kind>,<type>/zlecenie/<str:slug>,<int:pk>', views.SaleInvoiceCommissionCreateView.as_view(), name='sale_invoice_commission_create'),
    path('faktury/<str:kind>,<str:number>,<int:pk>/edycja', views.SaleInvoiceUpdateView.as_view(), name='sale_invoice_update'),
    path('faktury/korekta/<str:kind>,<str:number>,<int:pk>', views.CorrectiveSaleInvoiceCreateView.as_view(), name='sale_invoice_create_corrective'),
    path('faktury/<str:kind>,<str:number>,<int:pk>/edycja-korekty', views.CorrectiveSaleInvoiceUpdateView.as_view(), name='sale_invoice_update_corrective'),
    path('faktury/<str:kind>,<str:number>,<int:pk>.pdf', views.SaleInvoicePDFView.as_view(), name='sale_invoice_pdf'),
    path('faktury/<str:kind>,<str:number>,<int:pk>.pdf/drukuj', views.SaleInvoicePDFView.as_view(print_version=True), name='sale_invoice_print_pdf'),
    path('faktury/sprzedaz-czynnikow', views.ExportRefrigerantWeights.as_view(), name='export_refrigerant_weights'),
    path('sale_invoice_email', views.SendEmailView.as_view(), name='sale_invoice_email'),
    path('sale_invoice_set_payed/<int:pk>', views.SaleInvoiceSetPayed.as_view(), name='sale_invoice_set_payed'),

    path('uslugi', views.ServiceTemplateTableView.as_view(), name='service_templates'),
    path('uslugi/<str:name>,<int:pk>', views.ServiceTemplateDetailView.as_view(), name='service_template_detail'),
    path('uslugi/<str:name>,<int:pk>/edycja', views.ServiceTemplateUpdateView.as_view(), name='service_template_update'),
    path('uslugi/nowa', views.ServiceTemplateCreateView.as_view(), name='service_template_create'),
    path('service_autocomplete', views.ServiceTemplateAutocomplete.as_view(), name='service_template_autocomplete'),
    path('get_service_data', views.ServiceTemplateGetDataView.as_view(), name='get_service_template'),
    
    path('kontrahenci', views.ContractorTableView.as_view(), name='contractors'),
    path('kontrahenci/<str:name>,<int:pk>', views.ContractorDetailView.as_view(), name='contractor_detail'),
    path('kontrahenci/<str:name>,<int:pk>/edycja', views.ContractorUpdateView.as_view(), name='contractor_update'),
    path('kontrahenci/nowy', views.ContractorCreateView.as_view(), name='contractor_create'),
    path('contractors/<int:pk>/update_ajax', views.ContractorUpdateAjaxView.as_view(), name='contractor_update_ajax'),
    path('contractors/create_ajax', views.ContractorCreateAjaxView.as_view(), name='contractor_create_ajax'),
    path('contractor_gus', views.ContractorGUS.as_view(), name='contractor_gus'),
    path('contractor_autocomplete', views.ContractorAutocomplete.as_view(), name='contractor_autocomplete'),
    path('contractor_autocomplete_create', views.ContractorAutocomplete.as_view(modal_create=True), name='contractor_autocomplete_create'),
    path('get_contractor_data', views.ContractorGetDataView.as_view(), name='get_contractor'),
]
