from django.urls import include, path
from django.contrib import admin

from ariadne.contrib.django.views import GraphQLView
from django.views.decorators.cache import cache_page

from KlimaKar.views import (
    HomeView,
    SendIssueView,
    ChangeLogView,
    GarbageCollectionView,
    ScannerFormView,
)
from KlimaKar.graphql import schema


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("admin/defender/", include("defender.urls")),
    path("magazyn/", include("apps.warehouse.urls")),
    path("fakturowanie/", include("apps.invoicing.urls")),
    path("zlecenia/", include("apps.commission.urls")),
    path("statystyki/", include("apps.stats.urls")),
    path("ustawienia/", include("apps.settings.urls")),
    path("konta/", include("apps.accounts.urls")),
    path("audyt/", include("apps.audit.urls")),
    path("szukaj/", include("apps.search.urls")),
    path("wiki/", include("apps.wiki.urls")),
    path("pracownicy/", include("apps.employees.urls")),
    path("mycloudhome/", include("apps.mycloudhome.urls")),
    path("tiles/", include("tiles.urls")),
    path("send_issue", SendIssueView.as_view(), name="send_issue"),
    path("scanner_form", ScannerFormView.as_view(), name="scanner_form"),
    path(
        "garbage",
        cache_page(8 * 60 * 60)(GarbageCollectionView.as_view()),
        name="garbage",
    ),
    path("lista-zmian", ChangeLogView.as_view(), name="changelog"),
    path("django-rq/", include("django_rq.urls")),
    path(
        "graphql/",
        GraphQLView.as_view(
            schema=schema, playground_options={"request.credentials": "same-origin"}
        ),
        name="graphql",
    ),
]
