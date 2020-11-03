import django_filters

from django import forms
from apps.employees.models import Employee


class EmployeeFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )
    last_name = django_filters.CharFilter(
        lookup_expr="icontains", widget=forms.TextInput()
    )
    email = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())
    phone = django_filters.CharFilter(lookup_expr="icontains", widget=forms.TextInput())

    class Meta:
        model = Employee
        fields = ["first_name", "last_name", "email", "phone"]
