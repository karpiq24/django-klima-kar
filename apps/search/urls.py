from django.urls import path
from apps.search import views

app_name = "search"
urlpatterns = [
    path("", views.AjaxSearchView.as_view(), name="search"),
]
