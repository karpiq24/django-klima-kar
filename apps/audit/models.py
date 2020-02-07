import json

from django.contrib.contenttypes.models import ContentType
from django.db import models


class AuditLogManager(models.Manager):
    use_in_migrations = True

    def log_action(self, content_type, object_id, object_repr, action_type, diffrence=None):
        return self.model.objects.create(
            content_type=content_type,
            object_id=str(object_id),
            object_repr=object_repr[:200],
            action_type=action_type,
            diffrence=diffrence)


class AuditLog(models.Model):
    ADDITION = 'add'
    CHANGE = 'change'
    DELETION = 'delete'
    ACTION_TYPES = [
        (ADDITION, 'Dodanie'),
        (CHANGE, 'Zmiana'),
        (DELETION, 'Usunięcie'),
    ]

    action_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Czas akcji')
    content_type = models.ForeignKey(
        ContentType,
        models.SET_NULL,
        verbose_name='Typ obiektu',
        blank=True,
        null=True)
    object_id = models.TextField(
        verbose_name='ID obiektu',
        blank=True,
        null=True)
    object_repr = models.CharField(
        'Etykieta obiektu',
        max_length=200)
    action_type = models.CharField(
        max_length=6,
        choices=ACTION_TYPES,
        verbose_name='Typ akcji')
    diffrence = models.TextField(
        verbose_name='Zmiany',
        blank=True,
        null=True)

    objects = AuditLogManager()

    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logi'
        ordering = ('-action_time',)

    def __repr__(self):
        return str(self.action_time)

    def __str__(self):
        if self.is_addition():
            return f'Dodano {self.object_repr}'
        elif self.is_change():
            return f'Zmieniono {self.object_repr}'
        elif self.is_deletion():
            return f'Usunięto {self.object_repr}'

    def is_addition(self):
        return self.action_type == self.ADDITION

    def is_change(self):
        return self.action_type == self.CHANGE

    def is_deletion(self):
        return self.action_type == self.DELETION

    def get_diffrence(self, verbose=False):
        if not verbose:
            return json.loads(self.diffrence)
        diff = {}
        for key, values in self.get_diffrence().items():
            if self.action_type == self.CHANGE:
                values = [value if value is not None else '—' for value in values]
            diff[self._get_field_verbose_name(key)] = values
        return diff

    def _get_field_verbose_name(self, field):
        return self.content_type.model_class()._meta.get_field(field).verbose_name

    def get_edited_object(self):
        return self.content_type.get_object_for_this_type(pk=self.object_id)