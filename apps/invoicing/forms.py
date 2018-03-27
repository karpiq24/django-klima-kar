from dal import autocomplete

from django import forms
from django.urls import reverse

from apps.invoicing.models import Contractor, SaleInvoice, SaleInvoiceItem, ServiceTemplate
from apps.warehouse.models import Ware


class EnableDisableDateInput(forms.DateInput):
    template_name = 'invoicing/sale_invoice/date_field.html'


class SaleInvoiceModelForm(forms.ModelForm):
    contractor = forms.ModelChoiceField(
        label="Kontrahent",
        queryset=Contractor.objects.all(),
        widget=autocomplete.ModelSelect2(url='invoicing:contractor_autocomplete_create')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number'].widget.attrs.update({'placeholder': 'Podaj numer faktury'})
        self.fields['contractor'].widget.attrs.update({'data-placeholder': 'Wybierz kontrahenta'})
        self.fields['issue_date'].widget.attrs.update({'placeholder': 'Wybierz datę'})
        self.fields['issue_date'].widget.attrs.update({'class': 'date-input'})
        self.fields['completion_date'].widget.attrs.update({'placeholder': 'Wybierz datę'})
        self.fields['completion_date'].widget.attrs.update({'class': 'date-input'})
        self.fields['payment_date'].widget.attrs.update({'placeholder': 'Wybierz datę'})
        self.fields['payment_date'].widget.attrs.update({'class': 'date-input'})

    class Meta:
        model = SaleInvoice
        exclude = ['refrigerant_weidghts', 'number_value', 'number_year']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 1}),
            'payment_date': EnableDisableDateInput(),
            'invoice_type': forms.HiddenInput(),
            'total_value_netto': forms.HiddenInput(),
            'total_value_brutto': forms.HiddenInput()
        }


class NipInput(forms.TextInput):
    template_name = 'invoicing/contractor/nip_field.html'

    class Media:
        js = ('js/invoicing/contractor-gus.js',)

    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix')
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs, *args, **kwargs):
        context = super().get_context(name, value, attrs)
        context['url'] = reverse('invoicing:contractor_gus')
        context['prefix'] = self.prefix
        return context


class ContractorModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Podaj nazwę'})
        if self.instance and self.instance.nip_prefix:
            nip_prefix = self.instance.nip_prefix
        else:
            nip_prefix = ''
        self.fields['nip'].widget = NipInput(prefix=nip_prefix)
        self.fields['nip'].widget.attrs.update({'placeholder': 'Podaj NIP'})
        self.fields['address_1'].widget.attrs.update({'placeholder': 'Podaj adres'})
        self.fields['address_2'].widget.attrs.update({'placeholder': 'Podaj adres'})
        self.fields['city'].widget.attrs.update({'placeholder': 'Podaj miasto'})
        self.fields['postal_code'].widget.attrs.update({'placeholder': 'Podaj kod pocztowy'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Podaj adres e-mail'})

    class Meta:
        model = Contractor
        fields = ['nip_prefix', 'nip', 'name', 'city', 'postal_code', 'address_1', 'address_2', 'email']
        widgets = {
            'nip_prefix': forms.HiddenInput()
        }


class SaleInvoiceItemModelForm(forms.ModelForm):
    ware = forms.ModelChoiceField(
        label="Towar", queryset=Ware.objects.all(), required=False,
        widget=autocomplete.ModelSelect2(url='warehouse:ware_autocomplete')
    )
    service = forms.ModelChoiceField(
        label="Usługa", queryset=ServiceTemplate.objects.all(), required=False,
        widget=autocomplete.ModelSelect2(url='invoicing:service_template_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Podaj nazwę'})
        self.fields['name'].widget.attrs.update({'class': 'item-name'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Podaj opis'})
        self.fields['description'].widget.attrs.update({'class': 'item-description'})
        self.fields['quantity'].widget.attrs.update({'placeholder': 'Podaj ilość'})
        self.fields['quantity'].widget.attrs.update({'class': 'item-quantity'})
        self.fields['price_netto'].widget.attrs.update({'placeholder': 'Podaj cenę netto'})
        self.fields['price_netto'].widget.attrs.update({'class': 'item-netto'})
        self.fields['price_brutto'].widget.attrs.update({'placeholder': 'Podaj cenę brutto'})
        self.fields['price_brutto'].widget.attrs.update({'class': 'item-brutto'})
        self.fields['ware'].widget.attrs.update({'data-placeholder': 'Wybierz towar'})
        self.fields['ware'].widget.attrs.update({'class': 'item-ware'})
        self.fields['service'].widget.attrs.update({'data-placeholder': 'Wybierz usługę'})
        self.fields['service'].widget.attrs.update({'class': 'item-service'})

    class Meta:
        model = SaleInvoiceItem
        fields = ['name', 'description', 'quantity', 'price_netto', 'price_brutto', 'ware', 'service']


class ServiceTemplateModelForm(forms.ModelForm):
    ware = forms.ModelChoiceField(
        label="Towar", queryset=Ware.objects.all(), required=False,
        widget=autocomplete.ModelSelect2(url='warehouse:ware_autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Podaj nazwę'})
        self.fields['name'].widget.attrs.update({'class': 'item-name'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Podaj opis'})
        self.fields['description'].widget.attrs.update({'class': 'item-description'})
        self.fields['quantity'].widget.attrs.update({'placeholder': 'Podaj ilość'})
        self.fields['quantity'].widget.attrs.update({'class': 'item-quantity'})
        self.fields['price_netto'].widget.attrs.update({'placeholder': 'Podaj cenę netto'})
        self.fields['price_netto'].widget.attrs.update({'class': 'item-netto'})
        self.fields['price_brutto'].widget.attrs.update({'placeholder': 'Podaj cenę brutto'})
        self.fields['price_brutto'].widget.attrs.update({'class': 'item-brutto'})
        self.fields['ware'].widget.attrs.update({'data-placeholder': 'Wybierz towar'})
        self.fields['ware'].widget.attrs.update({'class': 'item-ware'})

    class Meta:
        model = ServiceTemplate
        fields = ['name', 'description', 'quantity', 'price_netto', 'price_brutto', 'ware']


class EmailForm(forms.Form):
    recipient = forms.EmailField(label='Do')
    subject = forms.CharField(label='Temat')
    message = forms.CharField(widget=forms.Textarea, label='Treść')
    sale_invoice = forms.ModelChoiceField(queryset=SaleInvoice.objects.none(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sale_invoice'].queryset = SaleInvoice.objects.filter(pk=self.initial['sale_invoice'].pk)
