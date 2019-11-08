# flake8: noqa
from django.urls import path
from django.views.generic.base import RedirectView
from apps.settings import views

app_name = 'settings'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='settings:email'), name='settings'),
    path('email', views.EmailSettingsUpdateView.as_view(), name='email'),
    path('fakturowanie', views.InvoicingSettingsUpdateView.as_view(), name='invoicing'),
    path('zlecenia', views.CommissionSettingsUpdateView.as_view(), name='commission'),
    path('mycloud', views.MyCloudHomeUpdateView.as_view(), name='mycloud'),
    path('mycloud_authorize', views.MyCloudHomeAuthorizeView.as_view(), name='mycloud_authorize'),
]
