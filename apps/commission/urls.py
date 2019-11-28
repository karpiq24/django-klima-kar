# flake8: noqa
from django.urls import path
from apps.commission import views
from apps.commission.models import Commission

app_name = 'commission'
urlpatterns = [
    path('pojazdy', views.VehicleTableView.as_view(), name='vehicles'),
    path('pojazdy/<str:slug>,<int:pk>', views.VehicleDetailView.as_view(), name='vehicle_detail'),
    path('pojazdy/<str:slug>,<int:pk>/edycja', views.VehicleUpdateView.as_view(), name='vehicle_update'),
    path('pojazdy/nowy', views.VehicleCreateView.as_view(), name='vehicle_create'),
    path('vehicle_autocomplete_create', views.VehicleAutocomplete.as_view(modal_create=True), name='vehicle_autocomplete_create'),
    path('vehicle_autocomplete', views.VehicleAutocomplete.as_view(), name='vehicle_autocomplete'),
    path('vehicles/<int:pk>/update_ajax', views.VehicleUpdateAjaxView.as_view(), name='vehicle_update_ajax'),
    path('vehicles/create_ajax', views.VehicleCreateAjaxView.as_view(), name='vehicle_create_ajax'),
    path('decode_aztec', views.DecodeAztecCode.as_view(), name='decode_aztec'),

    path('podzespoly', views.ComponentTableView.as_view(), name='components'),
    path('podzespoly/<str:slug>,<int:pk>', views.ComponentDetailView.as_view(), name='component_detail'),
    path('podzespoly/<str:slug>,<int:pk>/edycja', views.ComponentUpdateView.as_view(), name='component_update'),
    path('podzespoly/nowy', views.ComponentCreateView.as_view(), name='component_create'),
    path('component_autocomplete_create', views.ComponentAutocomplete.as_view(modal_create=True), name='component_autocomplete_create'),
    path('component_autocomplete', views.ComponentAutocomplete.as_view(), name='component_autocomplete'),
    path('components/<int:pk>/update_ajax', views.ComponentUpdateAjaxView.as_view(), name='component_update_ajax'),
    path('components/create_ajax', views.ComponentCreateAjaxView.as_view(), name='component_create_ajax'),

    path('', views.CommissionTableView.as_view(), name='commissions'),
    path('<str:slug>,<int:pk>', views.CommissionDetailView.as_view(), name='commission_detail'),
    path('<str:slug>,<int:pk>/pliki/<str:name>', views.CommissionFileDownloadView.as_view(), name='commission_file_download'),
    path('<str:slug>,<int:pk>/edycja', views.CommissionUpdateView.as_view(), name='commission_update'),
    path('<str:slug>,<int:pk>.pdf', views.CommissionPDFView.as_view(), name='commission_pdf'),
    path('<str:slug>,<int:pk>.pdf/drukuj', views.CommissionPDFView.as_view(print_version=True), name='commission_print_pdf'),
    path('nowe/pojazd', views.CommissionCreateView.as_view(commission_type=Commission.VEHICLE), name='commission_create_vehicle'),
    path('nowe/podzespol', views.CommissionCreateView.as_view(commission_type=Commission.COMPONENT), name='commission_create_component'),
    path('change_status', views.ChangeCommissionStatus.as_view(), name='change_status'),
    path('prepare_invoice_url', views.PrepareInvoiceUrl.as_view(), name='prepare_invoice_url'),
    path('commission_email', views.CommissionSendEmailView.as_view(), name='commission_email'),
    path('fast_commission', views.FastCommissionCreateView.as_view(), name='fast_commission'),
    path('commission_file_upload', views.CommissionFileUplaodView.as_view(), name='commission_file_upload'),
    path('delete_temp_file', views.DeleteTempFile.as_view(), name='delete_temp_file'),
    path('delete_commission_file', views.DeleteCommissionFile.as_view(), name='delete_commission_file'),
    path('check_upload', views.CheckUploadFinishedView.as_view(), name='check_upload'),
    path('assign_invoice', views.AssignInoiceView.as_view(), name='assign_invoice'),
    path('unassign_invoice', views.UnassignInoiceView.as_view(), name='unassign_invoice'),
    path('commission_autocomplete', views.CommissionAutocomplete.as_view(), name='commission_autocomplete'),
]
