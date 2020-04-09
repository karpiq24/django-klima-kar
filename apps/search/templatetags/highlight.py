import re

from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.filter()
def highlight(text, query):
    pattern = re.compile(f"({query})", re.IGNORECASE)
    highlighted = pattern.sub(r'<span class="highlighted">\1</span>', text)
    return mark_safe(highlighted)
