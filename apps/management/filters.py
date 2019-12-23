import django_filters

from dateutil import parser as date_parser

from django import forms
from django.contrib.auth.models import User

from apps.management.models import UserSession


class UserSessionFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(
        label='Użytkownik',
        queryset=User.objects.all())
    country = django_filters.CharFilter(
        lookup_expr='icontains')
    created = django_filters.CharFilter(
        method='created_filter',
        widget=forms.TextInput(attrs={'class': 'date-range-input'}))

    class Meta:
        model = UserSession
        fields = ['user', 'created']

    def created_filter(self, queryset, name, value):
        try:
            date_from, date_to = value.split(' - ')
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
        except ValueError:
            return queryset.none()
        return queryset.filter(
            created__date__gte=date_from,
            created__date__lte=date_to).distinct()


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(
        label='Nazwa użytkownika',
        lookup_expr='icontains')
    email = django_filters.CharFilter(
        lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['username', 'email']
