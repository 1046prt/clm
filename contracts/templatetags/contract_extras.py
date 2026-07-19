from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def status_badge(status):
    display = status.replace("_", " ").title()
    return mark_safe(f'<span class="badge badge-{status}">{display}</span>')


@register.filter
def severity_badge(severity):
    display = severity.title()
    return mark_safe(f'<span class="badge badge-{severity}">{display}</span>')


@register.filter
def severity_soft(severity):
    display = severity.title()
    return mark_safe(f'<span class="badge badge-{severity}-soft">{display}</span>')


@register.filter
def priority_badge(priority):
    display = priority.title()
    return mark_safe(f'<span class="badge badge-{priority}">{display}</span>')


@register.simple_tag
def url_replace(request, field, value):
    query_dict = request.GET.copy()
    query_dict[field] = value
    return query_dict.urlencode()


@register.filter
def currency(value):
    if value:
        return f"${value:,.0f}"
    return "--"
