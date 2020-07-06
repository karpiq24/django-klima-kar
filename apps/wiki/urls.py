from django.urls import path
from apps.wiki import views

app_name = "wiki"
urlpatterns = [
    path("artykuly", views.ArticleListView.as_view(), name="article_list"),
    path("artykuly/nowy", views.ArticleCreateView.as_view(), name="article_create"),
    path(
        "artykuly/<str:slug>,<int:pk>",
        views.ArticleDetailView.as_view(),
        name="article_detail",
    ),
    path(
        "artykuly/<str:slug>,<int:pk>/edycja",
        views.ArticleUpdateView.as_view(),
        name="article_update",
    ),
    path(
        "<str:slug>,<int:pk>/pliki/<str:name>",
        views.ArticleFileDownloadView.as_view(),
        name="article_file_download",
    ),
    path(
        "tags_autocomplete_create",
        views.TagAutocomplete.as_view(create_field="name"),
        name="tags_autocomplete_create",
    ),
    path(
        "tags_autocomplete", views.TagAutocomplete.as_view(), name="tags_autocomplete",
    ),
    path(
        "delete_commission_file",
        views.DeleteArticleFile.as_view(),
        name="delete_article_file",
    ),
    path(
        "check_upload",
        views.CheckArticleUploadFinishedView.as_view(),
        name="check_upload",
    ),
]
