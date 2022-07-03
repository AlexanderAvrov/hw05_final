from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Фильтр, который даёт возможность указывать CSS-класс в HTML-коде"""
    return field.as_widget(attrs={'class': css})
