from django import forms
from dal import autocomplete

from KlimaKar.forms import ToggleInput
from apps.settings.models import SiteSettings, MyCloudHome, InvoiceDownloadSettings
from apps.warehouse.models import Supplier


class EmailSettingsModelForm(forms.ModelForm):

    class Meta:
        model = SiteSettings
        fields = ['EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD', 'EMAIL_PORT', 'EMAIL_USE_TLS',
                  'EMAIL_USE_SSL', 'DEFAULT_FROM_EMAIL']
        widgets = {
            'EMAIL_HOST_PASSWORD': forms.PasswordInput(render_value=True),
            'EMAIL_USE_TLS': forms.Select(choices=((True, 'Tak'), (False, 'Nie'))),
            'EMAIL_USE_SSL': forms.Select(choices=((True, 'Tak'), (False, 'Nie')))
        }


class InvoicingSettingsModelForm(forms.ModelForm):

    class Meta:
        model = SiteSettings
        fields = ['SALE_INVOICE_TAX_PERCENT', 'SALE_INVOICE_TAX_PERCENT_WDT', 'SALE_INVOICE_EMAIL_TITLE',
                  'SALE_INVOICE_EMAIL_BODY']
        help_texts = {
            'SALE_INVOICE_EMAIL_TITLE': 'Zawiera dostęp do kontekstu faktury np. {{ invoice.number }}',
            'SALE_INVOICE_EMAIL_BODY': 'Zawiera dostęp do kontekstu faktury np. {{ invoice.contractor }}',
        }


class CommissionSettingsModelForm(forms.ModelForm):

    class Meta:
        model = SiteSettings
        fields = ['COMMISSION_EMAIL_TITLE', 'COMMISSION_EMAIL_BODY', 'COMMISSION_SMS_BODY']
        help_texts = {
            'COMMISSION_EMAIL_TITLE': 'Zawiera dostęp do kontekstu zlecenia np. {{ commission.number }}',
            'COMMISSION_EMAIL_BODY': 'Zawiera dostęp do kontekstu zlecenia np. {{ commission.contractor }}',
            'COMMISSION_SMS_BODY': 'Zawiera dostęp do kontekstu zlecenia np. {{ commission.vc_name }}',
        }


class InvoiceDownloadSettingsModelForm(forms.ModelForm):
    INTER_CARS_SUPPLIER = forms.ModelChoiceField(
        label='Dostawca Inter Cars',
        queryset=Supplier.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='warehouse:supplier_autocomplete_create'),
        required=False)
    DEKO_SUPPLIER = forms.ModelChoiceField(
        label='Dostawca Deko',
        queryset=Supplier.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='warehouse:supplier_autocomplete_create'),
        required=False)
    SAUTO_SUPPLIER = forms.ModelChoiceField(
        label='Dostawca S-Auto',
        queryset=Supplier.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='warehouse:supplier_autocomplete_create'),
        required=False)
    GORDON_SUPPLIER = forms.ModelChoiceField(
        label='Dostawca Gordon',
        queryset=Supplier.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='warehouse:supplier_autocomplete_create'),
        required=False)
    ZATOKA_SUPPLIER = forms.ModelChoiceField(
        label='Dostawca Zatoka',
        queryset=Supplier.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='warehouse:supplier_autocomplete_create'),
        required=False)

    class Meta:
        model = InvoiceDownloadSettings
        fields = '__all__'
        widgets = {
            'DOWNLOAD_INTER_CARS': ToggleInput,
            'DOWNLOAD_DEKO': ToggleInput,
            'DOWNLOAD_SAUTO': ToggleInput,
            'DOWNLOAD_GORDON': ToggleInput,
            'DOWNLOAD_ZATOKA': ToggleInput,
            'INTER_CARS_TOKEN': forms.PasswordInput(render_value=True),
            'DEKO_PASSWORD': forms.PasswordInput(render_value=True),
            'SAUTO_PASSWORD': forms.PasswordInput(render_value=True),
            'GORDON_PASSWORD': forms.PasswordInput(render_value=True),
            'ZATOKA_PASSWORD': forms.PasswordInput(render_value=True),
        }


class MyCloudHomeModelForm(forms.ModelForm):

    class Meta:
        model = MyCloudHome
        fields = '__all__'
        widgets = {
            'WD_CLIENT_SECRET': forms.PasswordInput(render_value=True),
            'REFRESH_TOKEN': forms.PasswordInput(render_value=True, attrs={'readonly': 'readonly'}),
            'ACCESS_TOKEN': forms.PasswordInput(render_value=True, attrs={'readonly': 'readonly'}),
            'USER_ID': forms.TextInput(attrs={'readonly': 'readonly'}),
            'DEVICE_ID': forms.TextInput(attrs={'readonly': 'readonly'}),
            'DEVICE_NAME': forms.TextInput(attrs={'readonly': 'readonly'}),
            'DEVICE_INTERNAL_URL': forms.TextInput(attrs={'readonly': 'readonly'}),
            'DEVICE_EXTERNAL_URL': forms.TextInput(attrs={'readonly': 'readonly'}),
            'APP_DIR_ID': forms.TextInput(attrs={'readonly': 'readonly'}),
            'COMMISSION_DIR_ID': forms.TextInput(attrs={'readonly': 'readonly'}),
            'BACKUP_DIR_ID': forms.TextInput(attrs={'readonly': 'readonly'}),
        }
