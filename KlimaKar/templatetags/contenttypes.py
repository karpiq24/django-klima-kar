from django.template import Library
from django.contrib.contenttypes.models import ContentType

register = Library()


@register.filter()
def content_type(instance):
    return ContentType.objects.get_for_model(instance).pk
