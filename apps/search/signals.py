import django_rq

from haystack.signals import BaseSignalProcessor
from haystack.utils import get_identifier
from django.db.models.signals import post_delete, post_save
from django.conf import settings

from apps.search.utils import update_document, remove_document, get_model


class RQSignalProcessor(BaseSignalProcessor):
    def setup(self):
        for connection in self.connections.connections_info.keys():
            for model in (
                self.connections[connection].get_unified_index().get_indexed_models()
            ):
                post_save.connect(self.enqueue_save, sender=model)
                post_delete.connect(self.enqueue_delete, sender=model)

    def teardown(self):
        post_save.disconnect(self.enqueue_save)
        post_delete.disconnect(self.enqueue_delete)

    def enqueue_save(self, sender, instance, **kwargs):
        if settings.HAYSTACK_ENABLE_INDEXING:
            django_rq.enqueue(update_document, get_identifier(instance))
            for rel in getattr(sender, "RELATED_MODELS", []):
                model = get_model(rel[0])
                objects = model.objects.filter(**{f"{rel[1]}": instance.pk})
                for obj in objects:
                    django_rq.enqueue(update_document, get_identifier(obj))

    def enqueue_delete(self, sender, instance, **kwargs):
        if settings.HAYSTACK_ENABLE_INDEXING:
            django_rq.enqueue(remove_document, get_identifier(instance))
            for rel in getattr(sender, "RELATED_MODELS", []):
                model = get_model(rel[0])
                objects = model.objects.filter(**{f"{rel[1]}": instance.pk})
                for obj in objects:
                    django_rq.enqueue(update_document, get_identifier(obj))
