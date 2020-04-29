import django_rq

from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from apps.search.models import SearchDocument


def get_model(model_path):
    parts = model_path.split(".")
    model_name = parts[-1]
    app_name = ".".join(parts[:-1])
    return apps.get_model(app_name, model_name)


def get_model_and_instance(content_type_pk, instance_pk):
    model = ContentType.objects.get_for_id(content_type_pk).model_class()
    return model, model.objects.get(pk=instance_pk)


def update_index(content_type_pk, instance_pk):
    model, instance = get_model_and_instance(content_type_pk, instance_pk)
    SearchDocument.reindex(instance)
    for rel in getattr(model, "RELATED_MODELS", []):
        model = get_model(rel[0])
        objects = model.objects.filter(**{f"{rel[1]}": instance_pk})
        for obj in objects:
            SearchDocument.reindex(obj)


def remove_from_index(content_type_pk, instance_pk):
    model = ContentType.objects.get_for_id(content_type_pk).model_class()
    SearchDocument.remove(content_type_pk, instance_pk)
    for rel in getattr(model, "RELATED_MODELS", []):
        model = get_model(rel[0])
        objects = model.objects.filter(**{f"{rel[1]}": instance_pk})
        for obj in objects:
            SearchDocument.reindex(obj)


def post_save_handler(sender, instance, **kwargs):
    model = instance._meta.model
    content_type = ContentType.objects.get_for_model(model)
    django_rq.enqueue(update_index, content_type.pk, instance.pk)


def pre_delete_handler(sender, instance, **kwargs):
    model = instance._meta.model
    content_type = ContentType.objects.get_for_model(model)
    django_rq.enqueue(remove_from_index, content_type.pk, instance.pk)


def update_parent_handler(sender, instance, **kwargs):
    parent = getattr(sender, "PARENT_FIELD", None)
    if parent:
        parent_obj = getattr(instance, parent)
        model = parent_obj._meta.model
        content_type = ContentType.objects.get_for_model(model)
        django_rq.enqueue(update_index, content_type.pk, parent_obj.pk)
