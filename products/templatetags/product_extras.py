from django import template

from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def replace_param(request, field, value):
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    params[field] = value
    return params.urlencode()

@register.filter
def format_price(value):
    return '${:,.2f}'.format(value)
