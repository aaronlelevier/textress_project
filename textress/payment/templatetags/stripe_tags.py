from django import template

register = template.Library()


@register.filter
def stripe_money(value):
    try:
        return '${:.2f}'.format(value/100.0)
    except TypeError:
        return '$0.00'

@register.filter
def format_phone(value):
    try:
        return "({}) {}-{}".format(value[2:5], value[5:8], value[8:])
    except (IndexError, TypeError):
        return None
