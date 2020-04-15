import django_filters

from dateutil import parser as date_parser

from django import forms
from django.contrib.contenttypes.models import ContentType

from apps.audit.models import AuditLog


class AuditLogFilter(django_filters.FilterSet):
    action_time = django_filters.CharFilter(
        method="action_time_filter",
        widget=forms.TextInput(attrs={"class": "date-range-input"}),
    )
    action_type = django_filters.ChoiceFilter(choices=AuditLog.ACTION_TYPES)
    content_type = django_filters.ChoiceFilter(
        choices=[
            (c.pk, c.model_class()._meta.verbose_name)
            for c in ContentType.objects.exclude(auditlog=None)
        ]
    )
    object_repr = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = AuditLog
        fields = ["action_time", "action_type", "content_type", "object_repr"]

    def action_time_filter(self, queryset, name, value):
        try:
            date_from, date_to = value.split(" - ")
            date_from = date_parser.parse(date_from, dayfirst=True).date()
            date_to = date_parser.parse(date_to, dayfirst=True).date()
        except ValueError:
            return queryset.none()
        return queryset.filter(
            action_time__date__gte=date_from, action_time__date__lte=date_to
        ).distinct()
