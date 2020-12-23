from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Annotation(models.Model):
    content_type = models.ForeignKey(
        ContentType, models.CASCADE, verbose_name="Typ obiektu",
    )
    object_id = models.TextField(verbose_name="ID obiektu")
    content_object = GenericForeignKey()
    contents = models.TextField(verbose_name="Treść")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Czas utworzenia")
    is_active = models.BooleanField(default=True, verbose_name="Aktywna")
    last_edited = models.DateTimeField(auto_now=True, verbose_name="Czas edycji")

    class Meta:
        verbose_name = "Notatka do obiektu"
        verbose_name_plural = "Notatki do obiektów"
        ordering = ["-created"]

    def __str__(self):
        return f"Notatka do {self.content_object}: {self.contents[:20]}"

    @property
    def was_edited(self):
        return (self.last_edited - self.created).total_seconds() > 1

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()
