# flake8: noqa
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from KlimaKar.views import HomeView, SendIssueView, SendSMSView
from KlimaKar.forms import KlimaKarAuthenticationForm

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('zaloguj/', auth_views.LoginView.as_view(authentication_form=KlimaKarAuthenticationForm), name='login'),
    path('wyloguj/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),

    path('magazyn/', include('apps.warehouse.urls')),
    path('fakturowanie/', include('apps.invoicing.urls')),
    path('zlecenia/', include('apps.commission.urls')),
    path('stats/', include('apps.stats.urls')),
    path('ustawienia/', include('apps.settings.urls')),
    path('zarzadzanie/', include('apps.management.urls')),

    path('send_issue', SendIssueView.as_view(), name='send_issue'),
    path('send_sms', SendSMSView.as_view(), name='send_sms'),

    path('django-rq/', include('django_rq.urls'))
]
