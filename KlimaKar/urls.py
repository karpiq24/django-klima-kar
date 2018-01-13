# flake8: noqa
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from KlimaKar.views import HomeView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login/'}, name='logout'),
    url(r'^admin/', admin.site.urls),

    url(r'^warehouse/', include('apps.warehouse.urls')),
    url(r'^stats/', include('apps.stats.urls'))
]
