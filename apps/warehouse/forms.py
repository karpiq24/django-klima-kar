from django import forms
from django.forms.formsets import BaseFormSet

from apps.warehouse.models import Ware, Invoice, Supplier, InvoiceItem


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
        fields = ['supplier', 'number', 'date']


class SupplierModelForm(BootstrapModelForm):
    def __init__(self, *args, **kwargs):
        super(SupplierModelForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Podaj nazwę'})

    class Meta:
        model = Supplier
        fields = ['name']


class InvoiceItemModelForm(BootstrapModelForm):
    def __init__(self, *args, **kwargs):
        super(InvoiceItemModelForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs.update({'placeholder': 'Podaj ilość'})
        self.fields['quantity'].widget.attrs.update({'class': 'form-control field-quantity'})
        self.fields['price'].widget.attrs.update({'placeholder': 'Podaj cenę'})
        self.fields['price'].widget.attrs.update({'class': 'form-control field-price'})
        self.fields['ware'].widget.attrs.update({'class': 'form-control field-index'})

    class Meta:
        model = InvoiceItem
        fields = ['ware', 'quantity', 'price']


class BaseInvoiceItemFormSet(BaseFormSet):
    def clean(self):
        wares = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                ware = form.cleaned_data.get('ware', None)
                quantity = form.cleaned_data.get('quantity', None)
                price = form.cleaned_data.get('price', None)

                if ware:
                    if ware in wares:
                        duplicates = True
                    wares.append(ware)

                if duplicates:
                    raise forms.ValidationError(
                        'Nie można dodać twóch takich samych towarów do jednej faktury.',
                        code='duplicate_ware'
                    )

                if not quantity:
                    raise forms.ValidationError(
                        'Kaźdy towar musi mieć podaną ilość.',
                        code='missing_quantity'
                    )
                elif quantity <= 0:
                    raise forms.ValidationError(
                        'Ilość musi być większa od 0.',
                        code='missing_quantity'
                    )

                if not price:
                    raise forms.ValidationError(
                        'Każdy towar musi mieć podaną cenę.',
                        code='missing_price'
                    )
