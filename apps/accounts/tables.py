import django_tables2 as tables

from django.contrib.auth.models import User
from django.utils.html import format_html

from apps.accounts.models import UserSession


class UserSessionTable(tables.Table):
    user = tables.Column(
        attrs={'th': {'width': '10%'}})
    user_agent = tables.Column(
        attrs={'th': {'width': '35%'}})
    client_ip = tables.Column(
        attrs={'th': {'width': '13%'}})
    country = tables.Column(
        attrs={'th': {'width': '12%'}})
    created = tables.Column(
        attrs={'th': {'width': '23%'}})
    actions = tables.TemplateColumn(
        attrs={'th': {'width': '7%'}},
        verbose_name="Akcje",
        template_name='accounts/user_session_actions.html',
        orderable=False,
        exclude_from_export=True)

    class Meta:
        model = UserSession
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['user', 'user_agent', 'client_ip', 'created', 'country', 'actions']
        order_by = 'created'
        empty_text = 'Brak sesji użytkowników'


class UserTable(tables.Table):
    username = tables.Column(
        attrs={'th': {'width': '15%'}})
    email = tables.Column(
        attrs={'th': {'width': '18%'}})
    is_active = tables.BooleanColumn(
        yesno=('', ''),
        attrs={'th': {'width': '10%'}})
    is_staff = tables.BooleanColumn(
        yesno=('', ''),
        verbose_name="Zespół",
        attrs={'th': {'width': '10%'}})
    is_superuser = tables.BooleanColumn(
        yesno=('', ''),
        verbose_name="Administrator",
        attrs={'th': {'width': '10%'}})
    is_boss = tables.BooleanColumn(
        yesno=('', ''),
        verbose_name="Szef",
        empty_values=(),
        attrs={'th': {'width': '10%'}})
    is_logged_in = tables.BooleanColumn(
        yesno=('', ''),
        verbose_name="Zalogowany",
        empty_values=(),
        attrs={'th': {'width': '10%'}})
    actions = tables.TemplateColumn(
        attrs={'th': {'width': '7%'}},
        verbose_name="Akcje",
        template_name='accounts/user_actions.html',
        orderable=False,
        exclude_from_export=True)

    class Meta:
        model = User
        attrs = {'class': 'table table-striped table-hover table-bordered'}
        fields = ['username', 'email', 'is_active', 'is_staff', 'is_superuser', 'is_boss', 'is_logged_in', 'actions']
        order_by = 'username'
        empty_text = 'Brak użytkowników'

    def render_is_boss(self, record):
        return self._render_bool(record.groups.filter(name='boss').exists())

    def render_is_logged_in(self, record):
        return self._render_bool(UserSession.objects.filter(user=record).exists())

    def _render_bool(self, boolean):
        if boolean:
            return format_html('<span class="true"></span>')
        else:
            return format_html('<span class="false"></span>')
