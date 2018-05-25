from django import forms
from django.db.models import Q

import django_filters
from dal import autocomplete
from dateutil import parser as date_parser

from apps.warehouse.models import Ware, Invoice, Supplier
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
    purchase_date = django_filters.CharFilter(method='purchase_date_filter', label="Data zakupu",
                                              widget=forms.TextInput(attrs={'class': 'date-range-input'}))

    class Meta:
        model = Ware
        fields = ['index', 'name', 'description', 'stock']

    def index_filter(self, queryset, name, value):
        return queryset.filter(Q(index__icontains=value) | Q(index_slug__icontains=Ware.slugify(value)))

    def purchase_date_filter(self, queryset, name, value):
        try:
            date_from, date_to = value.split(' - ')
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
        except ValueError:
            return queryset.none()
        return queryset.filter(invoiceitem__invoice__date__gte=date_from,
                               invoiceitem__invoice__date__lte=date_to).distinct()

    def supplier_filter(self, queryset, name, value):
        return queryset.filter(invoiceitem__invoice__supplier=value).distinct()

    def stock_filter(self, queryset, name, value):
        if value == '1':
            return queryset.filter(stock__gte=1)
        elif value == '2':
            return queryset.filter(stock__lte=0)


class InvoiceFilter(django_filters.FilterSet):
    supplier = django_filters.ModelChoiceFilter(queryset=Supplier.objects.all(),
                                                widget=autocomplete.ModelSelect2(url='warehouse:supplier_autocomplete'))
    number = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    date = django_filters.CharFilter(method='purchase_date_filter', label="Data zakupu",
                                     widget=forms.TextInput(attrs={'class': 'date-range-input'}))

    class Meta:
        model = Invoice
        fields = ['supplier', 'number']

    def purchase_date_filter(self, queryset, name, value):
        try:
            date_from, date_to = value.split(' - ')
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
        except ValueError:
            return queryset.none()
        return queryset.filter(date__gte=date_from, date__lte=date_to).distinct()


class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = Supplier
        fields = ['name']
