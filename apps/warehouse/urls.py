from django.conf.urls import url
from apps.warehouse.views import WareListView


urlpatterns = [
    url(r'^$', WareListView.as_view()),
]
