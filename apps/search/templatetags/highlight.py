import re

from django.template import Library
from django.utils.safestring import mark_safe

from KlimaKar.functions import strip_accents

register = Library()


@register.filter()
def highlight(text, query):
    words = [word.strip() for word in query.split(" ") if word.strip()]
    highlighted = text
    for word in words:
        pattern = re.compile(f"({strip_accents(word)})", re.IGNORECASE)
        highlighted = pattern.sub(r'<span class="highlighted">\1</span>', highlighted)
    return mark_safe(highlighted)
