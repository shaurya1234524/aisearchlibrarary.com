from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    """Return encoded querystring after replacing `field` with `value`.

    Usage in template:
        {% load query_transform %}
        <a href="?{% url_replace request 'page' 2 %}">Page 2</a>

    This preserves all existing GET parameters and replaces/sets the given field.
    """
    if not request:
        return ''

    params = request.GET.copy()
    params[field] = value
    return params.urlencode()
