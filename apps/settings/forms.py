from django import forms

from apps.settings.models import SiteSettings


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
