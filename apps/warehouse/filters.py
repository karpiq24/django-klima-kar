from django import forms

import django_filters

from apps.warehouse.models import Ware, Invoice, Supplier


class WareFilter(django_filters.FilterSet):
    index = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = django_filters.CharFilter(lookup_expr='icontains',
                                            widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Ware
        fields = ['index', 'name', 'description']


class InvoiceFilter(django_filters.FilterSet):
    supplier = django_filters.ModelChoiceFilter(queryset=Supplier.objects.all(),
                                                widget=forms.Select(attrs={'class': 'form-control'}))
    number = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'form-control'}))
    date__gte = django_filters.DateFilter(name='date', lookup_expr='gte', label="Data od",
                                          widget=forms.DateInput(attrs={'class': 'date-input form-control'}))
    date__lte = django_filters.DateFilter(name='date', lookup_expr='lte', label="Data do",
                                          widget=forms.DateInput(attrs={'class': 'date-input form-control'}))

    class Meta:
        model = Invoice
        fields = ['supplier', 'number']


class SupplierFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Supplier
        fields = ['name']
