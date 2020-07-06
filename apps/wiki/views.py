from urllib.parse import urlencode

from django.contrib import messages
from django.urls import reverse
from django.utils.text import slugify
from django.views.generic import DetailView
from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from KlimaKar.views import CustomSelect2QuerySetView, FilteredSingleTableView
from apps.mycloudhome.utils import check_and_enqueue_file_upload, get_temporary_files
from apps.mycloudhome.views import (
    FileDownloadView,
    CheckUploadFinishedView,
    DeleteSavedFile,
)
from apps.wiki.filters import ArticleFilter
from apps.wiki.forms import ArticleModelForm, ExternalLinkInline
from apps.wiki.models import Tag, Article, ArticleFile
from apps.wiki.tables import ArticleTable


class ArticleCreateView(CreateWithInlinesView):
    model = Article
    form_class = ArticleModelForm
    inlines = [ExternalLinkInline]
    template_name = "wiki/article/article_form.html"

    def forms_valid(self, form, inlines):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            '<a href="{}">Dodaj kolejny artykuł.</a>'.format(
                reverse("wiki:article_create")
            ),
        )
        check_and_enqueue_file_upload(form.data["upload_key"], self.object, ArticleFile)
        return super().forms_valid(form, inlines)

    def get_success_url(self, **kwargs):
        return reverse(
            "wiki:article_detail",
            kwargs={"pk": self.object.pk, "slug": slugify(self.object)},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upload_key = self.request.POST.get("upload_key")
        if upload_key:
            context["temp_files"] = get_temporary_files(upload_key)
        return context


class ArticleUpdateView(UpdateWithInlinesView):
    model = Article
    form_class = ArticleModelForm
    inlines = [ExternalLinkInline]
    template_name = "wiki/article/article_form.html"

    def forms_valid(self, form, inlines):
        messages.add_message(self.request, messages.SUCCESS, "Zapisano zmiany.")
        check_and_enqueue_file_upload(form.data["upload_key"], self.object, ArticleFile)
        return super().forms_valid(form, inlines)

    def get_success_url(self, **kwargs):
        return reverse(
            "wiki:article_detail",
            kwargs={"pk": self.object.pk, "slug": slugify(self.object)},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upload_key = self.request.POST.get("upload_key")
        if upload_key:
            context["temp_files"] = get_temporary_files(upload_key)
        return context


class ArticleListView(FilteredSingleTableView):
    model = Article
    table_class = ArticleTable
    paginate_by = 10
    template_name = "wiki/article/article_list.html"
    filter_class = ArticleFilter


class ArticleDetailView(DetailView):
    model = Article
    template_name = "wiki/article/article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        key = "{}_params".format(self.model.__name__)
        context["back_url"] = (
            reverse("wiki:article_list")
            + "?"
            + urlencode(self.request.session.get(key, ""))
        )
        return context


class TagAutocomplete(CustomSelect2QuerySetView):
    def get_queryset(self):
        qs = Tag.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class ArticleFileDownloadView(FileDownloadView):
    model = Article
    file_model = ArticleFile


class CheckArticleUploadFinishedView(CheckUploadFinishedView):
    model = Article
    file_download_url = "wiki:article_file_download"


class DeleteArticleFile(DeleteSavedFile):
    model = Article
    file_model = ArticleFile
