from django import forms

from apps.settings.models import SiteSettings, MyCloudHome


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
