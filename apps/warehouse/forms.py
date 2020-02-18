from django import forms

from dal import autocomplete
from extra_views import InlineFormSet

from apps.warehouse.models import Ware, Invoice, Supplier, InvoiceItem


class WareModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(WareModelForm, self).__init__(*args, **kwargs)
        self.fields['index'].widget.attrs.update({'placeholder': 'Podaj indeks'})
        self.fields['name'].widget.attrs.update({'placeholder': 'Podaj nazwę'})

    class Meta:
        model = Ware
        fields = ['index', 'name', 'description', 'stock', 'retail_price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    class Media:
        js = ('js/warehouse/ware.js',)


class InvoiceModelForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        label="Dostawca",
        queryset=Supplier.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='warehouse:supplier_autocomplete_create')
    )

    def __init__(self, *args, **kwargs):
        super(InvoiceModelForm, self).__init__(*args, **kwargs)
        self.fields['number'].widget.attrs.update({'placeholder': 'Podaj numer faktury'})
        self.fields['supplier'].widget.attrs.update({'data-placeholder': 'Wybierz dostawcę'})
        self.fields['date'].widget.attrs.update({'placeholder': 'Wybierz datę'})
        self.fields['date'].widget.attrs.update({'class': 'date-input'})

    class Meta:
        model = Invoice
        fields = ['supplier', 'number', 'date']


class SupplierModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SupplierModelForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Podaj nazwę'})

    class Meta:
        model = Supplier
        fields = ['name']


class InvoiceItemModelForm(forms.ModelForm):
    ware = forms.ModelChoiceField(
        queryset=Ware.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='warehouse:ware_autocomplete_create')
    )

    def __init__(self, *args, **kwargs):
        super(InvoiceItemModelForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs.update({'placeholder': 'Podaj ilość'})
        self.fields['quantity'].widget.attrs.update({'class': 'item-quantity'})
        self.fields['price'].widget.attrs.update({'placeholder': 'Podaj cenę'})
        self.fields['price'].widget.attrs.update({'class': 'item-price'})
        self.fields['ware'].widget.attrs.update({'class': 'item-ware'})
        self.fields['ware'].widget.attrs.update({'data-placeholder': 'Wybierz towar'})

    class Meta:
        model = InvoiceItem
        fields = ['ware', 'quantity', 'price']


class InvoiceItemsInline(InlineFormSet):
    model = InvoiceItem
    form_class = InvoiceItemModelForm
    factory_kwargs = {'extra': 20}
