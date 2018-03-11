# flake8: noqa
from django.urls import include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from KlimaKar.views import HomeView

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, {'next_page': 'login/'}, name='logout'),
    path('admin/', admin.site.urls),

    path('warehouse/', include('apps.warehouse.urls')),
    path('invoicing/', include('apps.invoicing.urls')),
    path('stats/', include('apps.stats.urls'))
]
