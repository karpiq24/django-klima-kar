import django_rq

from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from apps.search.models import SearchDocument


def reindex(content_type_pk, instance_pk):
    model = ContentType.objects.get_for_id(content_type_pk).model_class()
    instance = model.objects.get(pk=instance_pk)
    SearchDocument.reindex(instance)


def enqueue_reindex(instance):
    model = instance._meta.model
    content_type = ContentType.objects.get_for_model(model)
    django_rq.enqueue(reindex, content_type.pk, instance.pk)


def get_model(model_path):
    parts = model_path.split(".")
    model_name = parts[-1]
    app_name = ".".join(parts[:-1])
    return apps.get_model(app_name, model_name)


def post_save_handler(sender, instance, **kwargs):
    enqueue_reindex(instance)
    for rel in getattr(sender, "RELATED_MODELS", []):
        model = get_model(rel[0])
        objects = model.objects.filter(**{f"{rel[1]}": instance.pk})
        for obj in objects:
            enqueue_reindex(obj)


def pre_delete_handler(sender, instance, **kwargs):
    SearchDocument.remove(instance)
    for rel in getattr(sender, "RELATED_MODELS", []):
        model = get_model(rel[0])
        objects = model.objects.filter(**{f"{rel[1]}": instance.pk})
        for obj in objects:
            enqueue_reindex(obj)


def update_parent_handler(sender, instance, **kwargs):
    parent = getattr(sender, "PARENT_FIELD", None)
    if parent:
        enqueue_reindex(getattr(instance, parent))
