# coding=utf-8
from django import template

register = template.Library()


@register.filter()
def has_group(user, group):
    if user.is_superuser:
        return True
    if user.groups.filter(name=group).exists():
        return True
    return False
