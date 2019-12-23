# flake8: noqa
from django.urls import path
from apps.management import views

app_name = 'management'
urlpatterns = [
    path('sesje-uzytkownikow', views.UserSessionTableView.as_view(), name='user_sessions'),
    path('uzytkownicy', views.UserTableView.as_view(), name='users'),
    path('deletesession', views.DeleteUserSessionView.as_view(), name='delete_user_session'),
    path('deleteusersessions', views.DeleteUserSessionsView.as_view(), name='delete_user_sessions'),
]
