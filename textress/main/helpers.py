from django.core.exceptions import PermissionDenied


def get_user_hotel(user):
    '''
    AnonymousUser -or- Users that haven't fully set up the profile won't 
    have a hotel.
    '''
    try:
        return user.profile.hotel
    except AttributeError:
        raise PermissionDenied