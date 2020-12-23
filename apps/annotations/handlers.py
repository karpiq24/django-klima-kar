from django.contrib.contenttypes.models import ContentType

from apps.annotations.models import Annotation


def delete_annotations_handler(sender, instance, **kwargs):
    Annotation.objects.filter(
        content_type=ContentType.objects.get_for_model(instance._meta.model),
        object_id=instance.pk,
    ).delete()
