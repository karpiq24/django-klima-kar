
from django.views.generic import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from apps.management.tables import UserSessionTable, UserTable
from apps.management.models import UserSession
from apps.management.filters import UserSessionFilter, UserFilter
from apps.management.mixins import UserIsAdminMixin
from KlimaKar.views import FilteredSingleTableView


class UserSessionTableView(UserIsAdminMixin, FilteredSingleTableView):
    model = UserSession
    table_class = UserSessionTable
    filter_class = UserSessionFilter
    template_name = 'management/users/user_session_table.html'


class DeleteUserSessionView(UserIsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        user_session = get_object_or_404(UserSession, pk=request.POST.get('session'))
        user_session.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Sesja została usunięta.',
            }, status=200)


class DeleteUserSessionsView(UserIsAdminMixin, View):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.POST.get('user'))
        UserSession.delete_user_sessions(user)
        return JsonResponse({
            'status': 'success',
            'message': 'Sesje zostały usunięte.',
            }, status=200)


class UserTableView(UserIsAdminMixin, FilteredSingleTableView):
    model = User
    table_class = UserTable
    filter_class = UserFilter
    template_name = 'management/users/user_table.html'
