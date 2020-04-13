import re

from django.template import Library
from django.utils.safestring import mark_safe

from KlimaKar.functions import strip_accents

register = Library()


@register.filter()
def highlight(text, query):
    pattern = re.compile(f"({strip_accents(query)})", re.IGNORECASE)
    highlighted = pattern.sub(r'<span class="highlighted">\1</span>', text)
    return mark_safe(highlighted)
