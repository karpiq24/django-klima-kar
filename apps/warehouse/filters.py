from django import forms
from django.db.models import Q

import django_filters
from dal import autocomplete

from apps.warehouse.models import Ware, Invoice, Supplier, InvoiceItem
from apps.warehouse.dictionaries import STOCK_CHOICES


class WareFilter(django_filters.FilterSet):
    index = django_filters.CharFilter(method='index_filter', widget=forms.TextInput())
    name = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    description = django_filters.CharFilter(lookup_expr='icontains',
                                            widget=forms.TextInput())
    stock = django_filters.ChoiceFilter(choices=STOCK_CHOICES, method='stock_filter',
                                        widget=forms.Select())
    supplier = django_filters.ModelChoiceFilter(method='supplier_filter', queryset=Supplier.objects.all(),
                                                widget=autocomplete.ModelSelect2(url='warehouse:supplier_autocomplete'),
                                                label="Zakup od dostawcy")
    date__gte = django_filters.DateFilter(method='date_from_filter', label="Data zakupu od",
                                          widget=forms.DateInput(attrs={'class': 'date-input'}))
    date__lte = django_filters.DateFilter(method='date_to_filter', label="Data zakupu do",
                                          widget=forms.DateInput(attrs={'class': 'date-input'}))

    class Meta:
        model = Ware
        fields = ['index', 'name', 'description', 'stock']

    def index_filter(self, queryset, name, value):
        return queryset.filter(Q(index__icontains=value) | Q(index_slug__icontains=Ware.slugify(value)))

    def date_from_filter(self, queryset, name, value):
        to_include = InvoiceItem.objects.filter(invoice__date__gte=value).values_list('ware__id', flat=True)
        return queryset.filter(pk__in=to_include).exclude(invoiceitem=None)

    def date_to_filter(self, queryset, name, value):
        to_include = InvoiceItem.objects.filter(invoice__date__lte=value).values_list('ware__id', flat=True)
        return queryset.filter(pk__in=to_include).exclude(invoiceitem=None)

    def supplier_filter(self, queryset, name, value):
        to_include = InvoiceItem.objects.filter(invoice__supplier=value).values_list('ware__id', flat=True)
        return queryset.filter(pk__in=to_include).exclude(invoiceitem=None)

    def stock_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(stock__gte=1)
        elif value == '2':
            return queryset.filter(stock__lte=0)


class InvoiceFilter(django_filters.FilterSet):
    supplier = django_filters.ModelChoiceFilter(queryset=Supplier.objects.all(),
                                                widget=autocomplete.ModelSelect2(url='warehouse:supplier_autocomplete'))
    number = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    date__gte = django_filters.DateFilter(name='date', lookup_expr='gte', label="Data od",
                                          widget=forms.DateInput(attrs={'class': 'date-input'}))
    date__lte = django_filters.DateFilter(name='date', lookup_expr='lte', label="Data do",
                                          widget=forms.DateInput(attrs={'class': 'date-input'}))

    class Meta:
        model = Invoice
        fields = ['supplier', 'number']


class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = Supplier
        fields = ['name']
