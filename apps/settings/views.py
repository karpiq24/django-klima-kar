from django.views.generic import UpdateView, View
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse

from KlimaKar.mixins import GroupAccessControlMixin
from apps.settings.models import SiteSettings, MyCloudHome
from apps.settings.forms import EmailSettingsModelForm, InvoicingSettingsModelForm,\
    CommissionSettingsModelForm, MyCloudHomeModelForm


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


class MyCloudHomeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MyCloudHome
    form_class = MyCloudHomeModelForm
    template_name = 'settings/mycloud.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_object(self, queryset=None):
        return MyCloudHome.load()

    def get_success_url(self, **kwargs):
        return reverse("settings:mycloud")


class MyCloudHomeAuthorizeView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def post(self, *args, **kwargs):
        if not self.request.POST.get('code'):
            return JsonResponse({'status': 'error', 'message': 'Podaj kod autoryzacyjny.'}, status=400)
        cloud = MyCloudHome.load()
        if cloud.authorize_connection(self.request.POST.get('code')):
            messages.add_message(self.request, messages.SUCCESS, 'Autoryzacja zakończona powodzeniem.')
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Coś poszło nie tak. Spróbuj ponownie'}, status=400)
