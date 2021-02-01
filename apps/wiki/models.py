from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse

from KlimaKar.templatetags.slugify import slugify
from apps.audit.functions import get_audit_logs
from apps.mycloudhome.models import MyCloudHomeFile, MyCloudHomeDirectoryModel
from apps.search.models import SearchDocument


class Tag(models.Model):
    name = models.CharField(max_length=256, verbose_name="Nazwa")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tagi"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Article(MyCloudHomeDirectoryModel):
    AUDIT_IGNORE = ["upload", "mch_id", "scanning"]
    DIRECTORY_ID_FIELD = "ARTICLE_DIR_ID"
    MODEL_COLOR = "#0A3200"
    MODEL_ICON = "fa fa-book-open"

    tags = models.ManyToManyField(Tag, verbose_name="Tagi")
    title = models.CharField(max_length=256, verbose_name="Tytuł")
    description = models.TextField(verbose_name="Opis")
    contents = models.TextField(verbose_name="Treść")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="Czas dodania")
    edit_time = models.DateTimeField(auto_now=True, verbose_name="Czas edycji")

    search = GenericRelation(SearchDocument, related_query_name="article")

    class Meta:
        verbose_name = "Artykuł"
        verbose_name_plural = "Artykuły"
        ordering = ["-create_time"]

    def __str__(self):
        return self.title

    @property
    def main_image(self):
        return self.articlefile_set.filter(is_main_image=True).first()

    def get_absolute_url(self):
        return reverse(
            "wiki:article_detail", kwargs={"pk": self.pk, "slug": slugify(self)}
        )

    def get_files(self):
        return self.articlefile_set.all()

    def get_images(self):
        return self.articlefile_set.filter(
            mime_type__in=[
                "image/apng",
                "image/bmp",
                "image/gif",
                "image/x-icon",
                "image/jpeg",
                "image/png",
                "image/svg+xml",
                "image/tiff",
                "image/webp",
            ]
        )

    def get_logs(self):
        return get_audit_logs(
            self,
            has_annotations=False,
            m2one=[
                {
                    "key": "article",
                    "objects": self.externallink_set.all(),
                    "model": ExternalLink,
                },
                {
                    "key": "article",
                    "objects": self.articlefile_set.all(),
                    "model": ArticleFile,
                },
            ],
        )


class ExternalLink(models.Model):
    article = models.ForeignKey(
        Article, verbose_name="Artykuł", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=256, verbose_name="Nazwa")
    url = models.URLField(verbose_name="Adres URL")

    class Meta:
        verbose_name = "Zewnętrzny link"
        verbose_name_plural = "Zwenętrzne linki"
        ordering = ["pk"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            "wiki:article_detail", kwargs={"pk": self.article.pk, "slug": slugify(self)}
        )


class ArticleFile(MyCloudHomeFile):
    PARENT_FIELD = "article"

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, verbose_name="Artykuł"
    )
    is_main_image = models.BooleanField(default=False, verbose_name="Główny obrazek")

    class Meta:
        verbose_name = "Plik artykułu"
        verbose_name_plural = "Pliki artykułów"
        ordering = ["article", "pk"]

    def get_absolute_url(self):
        return reverse(
            "wiki:article_detail",
            kwargs={"pk": self.article.pk, "slug": slugify(self.article)},
        )

    def get_download_url(self):
        return reverse(
            "wiki:article_file_download",
            kwargs={
                "pk": self.article.pk,
                "slug": slugify(self.article),
                "name": self.file_name,
            },
        )
