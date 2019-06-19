from django import template

register = template.Library()


@register.simple_tag
def active(request, pattern):
    if pattern == request.path:
        return 'active'
    return ''


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()
