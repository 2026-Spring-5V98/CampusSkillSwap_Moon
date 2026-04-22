from django import template

register = template.Library()

@register.filter
def selected_if_equal(value1, value2):
    """
    Returns 'selected' if value1 equals value2, otherwise empty string.
    Used in templates to avoid template syntax errors with == comparisons.
    """
    if str(value1) == str(value2):
        return 'selected'
    return ''

@register.filter
def filter_available(queryset):
    """
    Filters a queryset of skills to return only those with availability='available'.
    Can be used as: {{ user_skills|filter_available }} to get the count.
    """
    try:
        return queryset.filter(availability='available').count()
    except (AttributeError, TypeError):
        return 0
