from django.views.generic import UpdateView, View, RedirectView
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse

from KlimaKar.mixins import GroupAccessControlMixin, SuperUserOnlyMixin
from apps.settings.models import SiteSettings, MyCloudHome, InvoiceDownloadSettings
from apps.settings.forms import (
    EmailSettingsModelForm,
    InvoicingSettingsModelForm,
    CommissionSettingsModelForm,
    MyCloudHomeModelForm,
    InvoiceDownloadSettingsModelForm,
)


class EmailSettingsUpdateView(GroupAccessControlMixin, UpdateView):
    allowed_groups = ["boss"]
    model = SiteSettings
    form_class = EmailSettingsModelForm
    template_name = "settings/email.html"

    def get_object(self, queryset=None):
        return SiteSettings.load()

    def get_success_url(self, **kwargs):
        return reverse("settings:email")


class InvoicingSettingsUpdateView(GroupAccessControlMixin, UpdateView):
    allowed_groups = ["boss"]
    model = SiteSettings
    form_class = InvoicingSettingsModelForm
    template_name = "settings/invoicing.html"

    def get_object(self, queryset=None):
        return SiteSettings.load()

    def get_success_url(self, **kwargs):
        return reverse("settings:invoicing")


class CommissionSettingsUpdateView(GroupAccessControlMixin, UpdateView):
    allowed_groups = ["boss"]
    model = SiteSettings
    form_class = CommissionSettingsModelForm
    template_name = "settings/commission.html"

    def get_object(self, queryset=None):
        return SiteSettings.load()

    def get_success_url(self, **kwargs):
        return reverse("settings:commission")


class InvoiceDownloadSettingsUpdateView(GroupAccessControlMixin, UpdateView):
    allowed_groups = ["boss"]
    model = InvoiceDownloadSettings
    form_class = InvoiceDownloadSettingsModelForm
    template_name = "settings/invoice_download.html"

    def get_object(self, queryset=None):
        return InvoiceDownloadSettings.load()

    def get_success_url(self, **kwargs):
        return reverse("settings:invoice_download")


class MyCloudHomeUpdateView(SuperUserOnlyMixin, UpdateView):
    model = MyCloudHome
    form_class = MyCloudHomeModelForm
    template_name = "settings/mycloud.html"

    def get_object(self, queryset=None):
        return MyCloudHome.load()

    def get_success_url(self, **kwargs):
        return reverse("settings:mycloud")


class MyCloudHomeInitializeView(SuperUserOnlyMixin, View):
    def post(self, *args, **kwargs):
        if not self.request.POST.get("code"):
            return JsonResponse(
                {"status": "error", "message": "Podaj kod autoryzacyjny."}, status=400
            )
        cloud = MyCloudHome.load()
        if cloud.authorize_connection(self.request.POST.get("code")):
            messages.add_message(
                self.request, messages.SUCCESS, "Autoryzacja zakończona powodzeniem."
            )
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse(
                {"status": "error", "message": "Coś poszło nie tak. Spróbuj ponownie"},
                status=400,
            )


class MyCloudRedirectAuthorizeView(SuperUserOnlyMixin, RedirectView):
    pattern_name = "settings:mycloud"
    query_string = True

    def test_func(self):
        return self.request.user.is_superuser


class MyCloudGetAuthUrl(SuperUserOnlyMixin, View):
    pattern_name = "settings:mycloud"

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, *args, **kwargs):
        cloud = MyCloudHome.load()
        return JsonResponse({"url": cloud.get_auth_url()}, status=200)
