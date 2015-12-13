from django import template
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist


register = template.Library() 


@register.filter
def has_group(user, group_name):
    '''
    Use to manage Group permissions to view within templates.
    '''
    try:
        group = Group.objects.get(name=group_name).name
    except ObjectDoesNotExist:
        group = None

    return True if group in user.groups.values_list('name', flat=True) else False


@register.filter
def proper_name(value):
    return value.replace('_',' ')
