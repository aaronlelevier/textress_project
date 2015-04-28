from django import template

register = template.Library()


@register.filter
def stripe_money(value):
    try:
        return '${:.2f}'.format(value/100.0)
    except TypeError:
        return '$0.00'
