from django.utils.text import slugify as _slugify
from django.template import Library

register = Library()


@register.filter()
def slugify(value):
    if not value:
        return ''
    value = value.replace('/', '-').replace('ł', 'l').replace('Ł', 'L')
    return _slugify(value)
