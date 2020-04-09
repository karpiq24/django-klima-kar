from django.apps import apps

from apps.search.models import SearchDocument


def get_model(model_path):
    parts = model_path.split(".")
    model_name = parts[-1]
    app_name = ".".join(parts[:-1])
    return apps.get_model(app_name, model_name)


def post_save_handler(sender, instance, **kwargs):
    SearchDocument.reindex(instance)
    for rel in getattr(sender, "RELATED_MODELS", []):
        model = get_model(rel[0])
        objects = model.objects.filter(**{f"{rel[1]}": instance.pk})
        for obj in objects:
            SearchDocument.reindex(obj)


def pre_delete_handler(sender, instance, **kwargs):
    SearchDocument.remove(instance)
    for rel in getattr(sender, "RELATED_MODELS", []):
        model = get_model(rel[0])
        objects = model.objects.filter(**{f"{rel[1]}": instance.pk})
        for obj in objects:
            SearchDocument.reindex(obj)


def update_parent_handler(sender, instance, **kwargs):
    parent = getattr(sender, "PARENT_FIELD", None)
    if parent:
        SearchDocument.reindex(getattr(instance, parent))
