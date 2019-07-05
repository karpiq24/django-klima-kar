import json

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library

register = Library()


@register.filter()
def to_list(messages):
    message_list = []
    for m in messages:
        message_list.append({'message': str(m), 'tag': m.tags})
    return message_list
