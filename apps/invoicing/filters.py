from django import forms

import django_filters
from dal import autocomplete

from apps.invoicing.models import SaleInvoice, Contractor, ServiceTemplate


class SaleInvoiceFilter(django_filters.FilterSet):
    contractor = django_filters.ModelChoiceFilter(
        queryset=Contractor.objects.all(), widget=autocomplete.ModelSelect2(
            url='invoicing:contractor_autocomplete'))
    number = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    issue_date__gte = django_filters.DateFilter(
        name='issue_date', lookup_expr='gte', label="Data wystawienia od",
        widget=forms.DateInput(attrs={'class': 'date-input'}))
    issue_date__lte = django_filters.DateFilter(
        name='issue_date', lookup_expr='lte', label="Data wystawienia do",
        widget=forms.DateInput(attrs={'class': 'date-input'}))
    completion_date__gte = django_filters.DateFilter(
        name='completion_date', lookup_expr='gte', label="Data wykonania od",
        widget=forms.DateInput(attrs={'class': 'date-input'}))
    completion_date__lte = django_filters.DateFilter(
        name='completion_date', lookup_expr='lte', label="Data wykonania do",
        widget=forms.DateInput(attrs={'class': 'date-input'}))

    class Meta:
        model = SaleInvoice
        fields = ['contractor', 'number']


class ContractorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    nip = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    address_1 = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    city = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    postal_code = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    email = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = Contractor
        fields = ['name', 'nip', 'address_1', 'city', 'postal_code', 'email']


class ServiceTemplateFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())
    description = django_filters.CharFilter(lookup_expr='icontains', widget=forms.TextInput())

    class Meta:
        model = ServiceTemplate
        fields = ['name', 'description']
