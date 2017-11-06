# flake8: noqa
from django.conf.urls import url, include
from django.contrib import admin
from KlimaKar.views import HomeView

urlpatterns = [
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^admin/', admin.site.urls),
    url(r'^warehouse/', include('apps.warehouse.urls'))
]
