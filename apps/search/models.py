from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.template.loader import get_template

from KlimaKar.functions import strip_accents


class SearchDocument(models.Model):
    content_type = models.ForeignKey(
        ContentType, models.CASCADE, verbose_name="Typ obiektu"
    )
    object_id = models.TextField(verbose_name="ID obiektu")
    content_object = GenericForeignKey()
    object_repr = models.CharField("Etykieta obiektu", max_length=200)
    text = models.TextField(verbose_name="Tekstowa treść obiektu")
    text_search = SearchVectorField(null=True, verbose_name="Wektor wyszukiwania")

    class Meta:
        verbose_name = "Dokument wyszukiwania"
        verbose_name_plural = "Dokumenty wyszukiwania"
        indexes = [GinIndex(fields=["text_search"])]

    def __str__(self):
        return f"Dokument: {self.object_repr}"

    @staticmethod
    def reindex(instance):
        model = instance._meta.model
        template = get_template(
            f"search/indexes/{model._meta.app_label}/{model._meta.model_name}_text.txt"
        )
        SearchDocument.objects.update_or_create(
            content_type=ContentType.objects.get_for_model(model),
            object_id=str(instance.pk),
            defaults={
                "object_repr": str(instance),
                "text": strip_accents(template.render({"object": instance})),
            },
        )

    @staticmethod
    def remove(conent_type_pk, instance_pk):
        try:
            SearchDocument.objects.get(
                content_type__pk=conent_type_pk, object_id=str(instance_pk),
            ).delete()
        except SearchDocument.DoesNotExist:
            pass
