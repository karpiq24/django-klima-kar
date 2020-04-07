import django_filters

from dal import autocomplete
from dateutil import parser as date_parser

from django import forms

from apps.commission.models import Vehicle, Component, Commission
from apps.invoicing.models import Contractor


class VehicleFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    model = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    registration_plate = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )
    vin = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    production_year = django_filters.CharFilter(
        lookup_expr="exact", widget=forms.TextInput()
    )

    class Meta:
        model = Vehicle
        fields = ["brand", "model", "registration_plate", "vin", "production_year"]


class ComponentFilter(django_filters.FilterSet):
    component_type = django_filters.ChoiceFilter(choices=Component.TYPE_CHOICES)
    model = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    serial_number = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )
    catalog_number = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )

    class Meta:
        model = Component
        fields = ["component_type", "model", "serial_number", "catalog_number"]


class CommissionFilter(django_filters.FilterSet):
    YES = "yes"
    NO = "no"
    YESNO = [(YES, "Tak"), (NO, "Nie")]

    status = django_filters.CharFilter(widget=forms.HiddenInput())
    pk = django_filters.CharFilter(
        lookup_expr="iexact", widget=forms.TextInput(), label="Numer zlecenia"
    )
    vc_name = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput(), label="Pojazd/podzespół"
    )
    contractor = django_filters.ModelChoiceFilter(
        queryset=Contractor.objects.all(),
        widget=autocomplete.ModelSelect2(url="invoicing:contractor_autocomplete"),
    )
    description = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )
    start_date = django_filters.CharFilter(
        method="start_date_filter",
        label="Data przyjęcia",
        widget=forms.TextInput(attrs={"class": "date-range-input"}),
    )
    end_date = django_filters.CharFilter(
        method="end_date_filter",
        label="Data zamknięcia",
        widget=forms.TextInput(attrs={"class": "date-range-input"}),
    )
    has_files = django_filters.ChoiceFilter(
        choices=YESNO, label="Załączono pliki", method="has_files_filter"
    )
    has_invoice = django_filters.ChoiceFilter(
        choices=YESNO, label="Przypisano fakturę", method="has_invoice_filter",
    )

    class Meta:
        model = Commission
        fields = [
            "status",
            "pk",
            "vc_name",
            "contractor",
            "description",
            "start_date",
            "end_date",
            "has_files",
            "has_invoice",
        ]

    def has_files_filter(self, queryset, name, value):
        if value == self.YES:
            return queryset.exclude(commissionfile=None)
        elif value == self.NO:
            return queryset.filter(commissionfile=None)

    def has_invoice_filter(self, queryset, name, value):
        if value == self.YES:
            return queryset.exclude(sale_invoices=None)
        elif value == self.NO:
            return queryset.filter(sale_invoices=None)

    def start_date_filter(self, queryset, name, value):
        try:
            date_from, date_to = value.split(" - ")
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
        except ValueError:
            return queryset.none()
        return queryset.filter(
            start_date__gte=date_from, start_date__lte=date_to
        ).distinct()

    def end_date_filter(self, queryset, name, value):
        try:
            date_from, date_to = value.split(" - ")
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
        except ValueError:
            return queryset.none()
        return queryset.filter(
            end_date__gte=date_from, end_date__lte=date_to
        ).distinct()
