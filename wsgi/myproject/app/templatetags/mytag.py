from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def settings_val(key):
    "Get the constant from settings file"
    return getattr(settings, key, "")
