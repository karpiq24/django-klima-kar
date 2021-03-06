from django import forms
from django.db.models import Q

import django_filters
from dal import autocomplete
from dateutil import parser as date_parser

from apps.invoicing.models import SaleInvoice, Contractor, ServiceTemplate


class SaleInvoiceFilter(django_filters.FilterSet):
    YES = "yes"
    NO = "no"
    REFRIGERANT_FILLED = [(YES, "Tak"), (NO, "Nie")]
    HAS_COMMISSION = [(YES, "Tak"), (NO, "Nie")]

    invoice_type = django_filters.CharFilter(widget=forms.HiddenInput())
    contractor = django_filters.ModelChoiceFilter(
        queryset=Contractor.objects.all(),
        widget=autocomplete.ModelSelect2(url="invoicing:contractor_autocomplete"),
    )
    number = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )
    payment_type = django_filters.ChoiceFilter(choices=SaleInvoice.PAYMENT_TYPES)
    refrigerant_filled = django_filters.ChoiceFilter(
        choices=REFRIGERANT_FILLED,
        label="Uzupełniono czynnik",
        method="refrigerant_filled_filter",
    )
    has_commission = django_filters.ChoiceFilter(
        choices=HAS_COMMISSION,
        label="Przypisano zlecenie",
        method="has_commission_filter",
    )
    issue_date = django_filters.CharFilter(
        method="issue_date_filter",
        label="Data wystawienia",
        widget=forms.TextInput(attrs={"class": "date-range-input"}),
    )
    created_date = django_filters.CharFilter(
        method="created_date_filter", label="", widget=forms.HiddenInput()
    )

    class Meta:
        model = SaleInvoice
        fields = ["invoice_type", "contractor", "number"]

    def refrigerant_filled_filter(self, queryset, name, value):
        if value == self.YES:
            return queryset.filter(
                Q(refrigerantweights__r134a__gt=0)
                | Q(refrigerantweights__r1234yf__gt=0)
                | Q(refrigerantweights__r12__gt=0)
                | Q(refrigerantweights__r404__gt=0)
            )
        elif value == self.NO:
            return queryset.exclude(
                Q(refrigerantweights__r134a__gt=0)
                | Q(refrigerantweights__r1234yf__gt=0)
                | Q(refrigerantweights__r12__gt=0)
                | Q(refrigerantweights__r404__gt=0)
            )

    def has_commission_filter(self, queryset, name, value):
        if value == self.YES:
            return queryset.exclude(commission=None)
        elif value == self.NO:
            return queryset.filter(commission=None)

    def issue_date_filter(self, queryset, name, value):
        try:
            date_from, date_to = value.split(" - ")
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
        except ValueError:
            return queryset.none()
        return queryset.filter(
            issue_date__gte=date_from, issue_date__lte=date_to
        ).distinct()

    def created_date_filter(self, queryset, name, value):
        try:
            date_from, date_to = value.split(" - ")
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
        except ValueError:
            return queryset.none()
        return queryset.filter(
            created_date__date__gte=date_from, created_date__date__lte=date_to
        ).distinct()


class ContractorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    nip = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    address_1 = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )
    city = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    postal_code = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )
    email = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    phone = django_filters.CharFilter(
        method="phone_filter", label="Numer telefonu", widget=forms.TextInput()
    )
    created_date = django_filters.CharFilter(
        method="created_date_filter", label="", widget=forms.HiddenInput()
    )

    class Meta:
        model = Contractor
        fields = ["name", "nip", "address_1", "city", "postal_code", "email", "phone"]

    def created_date_filter(self, queryset, name, value):
        try:
            date_from, date_to = value.split(" - ")
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
        except ValueError:
            return queryset.none()
        return queryset.filter(
            created_date__date__gte=date_from, created_date__date__lte=date_to
        ).distinct()

    def phone_filter(self, queryset, name, value):
        return queryset.filter(
            Q(phone_1__icontains=value) | Q(phone_2__icontains=value)
        )


class ServiceTemplateFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    description = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )

    class Meta:
        model = ServiceTemplate
        fields = ["name", "description"]
