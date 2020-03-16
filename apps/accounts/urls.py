from django.urls import path
from django.contrib.auth import views as auth_views

from apps.accounts import views
from apps.accounts.forms import KlimaKarAuthenticationForm

app_name = "accounts"
urlpatterns = [
    path(
        "zaloguj/",
        auth_views.LoginView.as_view(authentication_form=KlimaKarAuthenticationForm),
        name="login",
    ),
    path(
        "first_step_login/", views.FirstStepLoginView.as_view(), name="first_step_login"
    ),
    path("wyloguj/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "sesje-uzytkownikow", views.UserSessionTableView.as_view(), name="user_sessions"
    ),
    path("uzytkownicy", views.UserTableView.as_view(), name="users"),
    path(
        "deletesession",
        views.DeleteUserSessionView.as_view(),
        name="delete_user_session",
    ),
    path(
        "deleteusersessions",
        views.DeleteUserSessionsView.as_view(),
        name="delete_user_sessions",
    ),
]
