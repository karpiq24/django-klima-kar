import django_rq
import defender

from django.views.generic import View
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings

from apps.accounts.tables import UserSessionTable, UserTable
from apps.accounts.models import UserSession
from apps.accounts.filters import UserSessionFilter, UserFilter
from apps.accounts.mixins import UserIsAdminMixin
from apps.accounts.functions import send_token_email
from KlimaKar.views import FilteredSingleTableView


class UserSessionTableView(UserIsAdminMixin, FilteredSingleTableView):
    model = UserSession
    table_class = UserSessionTable
    filter_class = UserSessionFilter
    template_name = 'accounts/user_session_table.html'


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
    template_name = 'accounts/user_table.html'


class FirstStepLoginView(View):
    def post(self, request, *args, **kwargs):
        if not request.is_ajax:
            return HttpResponseForbidden()
        username = request.POST.get('username')
        password = request.POST.get('password')

        if defender.utils.is_already_locked(request, username=username):
            return self._account_locked_response()

        user, user_not_blocked = self._authenticate(request, username, password)

        if not user_not_blocked:
            return self._account_locked_response()
        if not user:
            return JsonResponse({
                'status': 'error',
                'message': 'Podana nazwa użytkownika lub hasło są nieprawidłowe.'
                }, status=401)
        if settings.TWO_STEP_LOGIN_ENABLED and user.email:
            django_rq.enqueue(send_token_email, user)
            return JsonResponse({
                'status': 'success',
                'code': 'token',
                'message': 'Token autoryzacyjny jest wymagany.'
                }, status=200)
        return JsonResponse({
                'status': 'success',
                'code': 'login_success',
                'message': 'Dane logowania prawidłowe.'
                }, status=200)

    def _authenticate(self, request, username, password):
        user = authenticate(request, username=username, password=password)

        defender.utils.add_login_attempt_to_db(
            request,
            login_valid=True if user else False,
            username=username)

        user_not_blocked = defender.utils.check_request(
            request,
            login_unsuccessful=False if user else True,
            username=username)
        return user, user_not_blocked

    def _account_locked_response(self):
        message = (
            f'Nieudana próba logowania nastąpiła już {defender.config.FAILURE_LIMIT} razy.\n'
            f'Twoje konto zostało zablokowane na {defender.config.COOLOFF_TIME} sekund.'
        )
        return JsonResponse({
            'status': 'error',
            'message': message,
            'blocked': True
            }, status=401)
