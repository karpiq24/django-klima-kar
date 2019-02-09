# flake8: noqa
from django.urls import path
from django.views.generic.base import RedirectView
from apps.settings import views

app_name = 'settings'
urlpatterns = [
    path('', RedirectView.as_view(pattern_name='settings:email'), name='settings'),
    path('email', views.EmailSettingsUpdateView.as_view(), name='email'),
    path('invoicing', views.InvoicingSettingsUpdateView.as_view(), name='invoicing'),
]
