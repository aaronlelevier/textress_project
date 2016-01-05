import calendar

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


@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]


@register.filter
def format_snake_case(snake_case):
    return snake_case.replace('_',' ')


@register.filter
def first_word(words):
    try:
        return words.split(' ')[0]
    except IndexError:
        return
