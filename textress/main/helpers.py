from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.models import Group


def get_user_hotel(user):
    """
    AnonymousUser -or- Users that haven't fully set up 
    the profile won't have a hotel.
    """
    try:
        return user.profile.hotel
    except AttributeError:
        raise PermissionDenied


def user_in_group(user, group_name):
    if group_name in user.groups.values_list('name', flat=True):
        return True
    else:
        return False
