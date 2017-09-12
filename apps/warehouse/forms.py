from django import forms

from apps.warehouse.models import Ware, Invoice, Supplier


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })


class WareModelForm(BootstrapModelForm):
    def __init__(self, *args, **kwargs):
        super(WareModelForm, self).__init__(*args, **kwargs)
        self.fields['index'].widget.attrs.update({'placeholder': 'Podaj indeks'})
        self.fields['name'].widget.attrs.update({'placeholder': 'Podaj nazwę'})
        self.fields['description'].widget.attrs.update({'placeholder': 'Podaj opis'})

    class Meta:
        model = Ware
        fields = ['index', 'name', 'description', 'stock']


class InvoiceModelForm(BootstrapModelForm):
    def __init__(self, *args, **kwargs):
        super(InvoiceModelForm, self).__init__(*args, **kwargs)
        self.fields['number'].widget.attrs.update({'placeholder': 'Podaj numer faktury'})
        self.fields['date'].widget.attrs.update({'placeholder': 'Wybierz datę'})
        self.fields['date'].widget.attrs.update({'class': 'date-input form-control'})

    class Meta:
        model = Invoice
        fields = ['supplier', 'number', 'date', 'items']


class SupplierModelForm(BootstrapModelForm):
    def __init__(self, *args, **kwargs):
        super(SupplierModelForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Podaj nazwę'})

    class Meta:
        model = Supplier
        fields = ['name']