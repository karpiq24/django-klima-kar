# flake8: noqa
from django.urls import path
from django.views.generic.base import RedirectView
from apps.settings import views

app_name = "settings"
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="settings:email"), name="settings"),
    path("email", views.EmailSettingsUpdateView.as_view(), name="email"),
    path("fakturowanie", views.InvoicingSettingsUpdateView.as_view(), name="invoicing"),
    path("zlecenia", views.CommissionSettingsUpdateView.as_view(), name="commission"),
    path(
        "pobieranie-faktur",
        views.InvoiceDownloadSettingsUpdateView.as_view(),
        name="invoice_download",
    ),
    path("mycloud", views.MyCloudHomeUpdateView.as_view(), name="mycloud"),
    path("get_auth_url", views.MyCloudGetAuthUrl.as_view(), name="get_auth_url"),
    path(
        "mycloud_authorize/",
        views.MyCloudRedirectAuthorizeView.as_view(),
        name="mycloud_authorize",
    ),
    path(
        "mycloud_initialize",
        views.MyCloudHomeInitializeView.as_view(),
        name="mycloud_initialize",
    ),
]
