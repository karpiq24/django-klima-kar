from django.contrib.contenttypes.models import ContentType

from apps.annotations.models import Annotation

from apps.annotations.graphql.types import mutation


@mutation.field("addAnnotation")
def resolve_add_annotation(_, info, app_name, model_name, object_id, contents):
    try:
        content_type = ContentType.objects.get(app_label=app_name, model=model_name)
        model = content_type.model_class()
        obj = model.objects.get(pk=object_id)
    except (ContentType.DoesNotExist, model.DoesNotExist):
        return None
    return obj.annotations.create(contents=contents)


@mutation.field("updateAnnotation")
def resolve_update_annotation(_, info, pk, contents, is_active):
    try:
        note = Annotation.objects.get(pk=pk)
    except Annotation.DoesNotExist:
        return None
    note.contents = contents
    note.is_active = is_active
    note.save()
    return note
