from django.views.generic import UpdateView
from django.urls import reverse

from KlimaKar.mixins import GroupAccessControlMixin
from apps.settings.models import SiteSettings
from apps.settings.forms import EmailSettingsModelForm, InvoicingSettingsModelForm,\
    CommissionSettingsModelForm


class EmailSettingsUpdateView(GroupAccessControlMixin, UpdateView):
    allowed_groups = ['boss']
    model = SiteSettings
    form_class = EmailSettingsModelForm
    template_name = 'settings/email.html'

    def get_object(self, queryset=None):
        return SiteSettings.load()

    def get_success_url(self, **kwargs):
        return reverse("settings:email")


class InvoicingSettingsUpdateView(GroupAccessControlMixin, UpdateView):
    allowed_groups = ['boss']
    model = SiteSettings
    form_class = InvoicingSettingsModelForm
    template_name = 'settings/invoicing.html'

    def get_object(self, queryset=None):
        return SiteSettings.load()

    def get_success_url(self, **kwargs):
        return reverse("settings:invoicing")


class CommissionSettingsUpdateView(GroupAccessControlMixin, UpdateView):
    allowed_groups = ['boss']
    model = SiteSettings
    form_class = CommissionSettingsModelForm
    template_name = 'settings/commission.html'

    def get_object(self, queryset=None):
        return SiteSettings.load()

    def get_success_url(self, **kwargs):
        return reverse("settings:commission")
