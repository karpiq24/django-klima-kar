from django.urls import include, path
from django.contrib import admin

from ariadne.contrib.django.views import GraphQLView

from KlimaKar.views import HomeView, SendIssueView, SendSMSView
from KlimaKar.graphql import schema

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('admin/defender/', include('defender.urls')),

    path('magazyn/', include('apps.warehouse.urls')),
    path('fakturowanie/', include('apps.invoicing.urls')),
    path('zlecenia/', include('apps.commission.urls')),
    path('stats/', include('apps.stats.urls')),
    path('ustawienia/', include('apps.settings.urls')),
    path('konta/', include('apps.accounts.urls')),
    path('audyt/', include('apps.audit.urls')),
    path('szukaj/', include('apps.search.urls')),

    path('tiles/', include('tiles.urls')),

    path('send_issue', SendIssueView.as_view(), name='send_issue'),
    path('send_sms', SendSMSView.as_view(), name='send_sms'),

    path('django-rq/', include('django_rq.urls')),
    path('graphql/', GraphQLView.as_view(
        schema=schema, playground_options={'request.credentials': 'same-origin'}), name='graphql'),
]
