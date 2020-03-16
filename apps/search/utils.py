from haystack.exceptions import NotHandled
from haystack.constants import DEFAULT_ALIAS
from haystack import connections

from django.apps import apps


def update_document(object_id):
    model, index, instance = get_model_instance_index(object_id)
    if not instance or not index:
        return
    index._get_backend(DEFAULT_ALIAS).update(index, [instance])


def remove_document(object_id):
    model, index, instance = get_model_instance_index(object_id)
    if not index:
        return
    index.remove_object(object_id, using=DEFAULT_ALIAS)


def get_model_instance_index(object_id):
    parts = object_id.split(".")
    pk = parts[-1]
    model_name = parts[-2]
    app_name = ".".join(parts[:-2])
    model = apps.get_model(app_name, model_name)
    try:
        index = connections[DEFAULT_ALIAS].get_unified_index().get_index(model)
    except NotHandled:
        index = None
    try:
        return model, index, model.objects.get(pk=pk)
    except model.DoesNotExist:
        return model, index, None


def get_model(model_path):
    parts = model_path.split(".")
    model_name = parts[-1]
    app_name = ".".join(parts[:-1])
    return apps.get_model(app_name, model_name)
