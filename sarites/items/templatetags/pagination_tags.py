from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return mark_safe(query.urlencode())

@register.simple_tag(takes_context=True)
def url_replace_page(context, param_name, page_number):
    query = context['request'].GET.copy()
    query[param_name] = page_number
    return mark_safe(query.urlencode())
