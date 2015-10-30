from django.core.exceptions import PermissionDenied

from rest_framework import permissions


'''
Instructions
------------
Must be Authenticated.

Must be a Manager or Admin to access any REST EndPoint.

Can Only Access one's own Hotel Records.
'''

class IsHotelObject(permissions.BasePermission):
    '''Confirm that the Object's Hotel is the same as the 
    User's Hotel.

    Ex: `guest.hotel`
    '''
    def has_object_permission(self, request, view, obj):
        try:
            hotel = request.user.profile.hotel
        except AttributeError:
            raise PermissionDenied
        return obj.hotel == request.user.profile.hotel


class IsManagerOrAdmin(permissions.BasePermission):
    '''
    Must be a Manager or Admin to access any REST EndPoint.
    '''
    def has_permission(self, request, view):
        return (request.user.is_superuser or
                request.user.groups.filter(name__in=["hotel_admin", "hotel_manager"]))


class IsHotelUser(permissions.BasePermission):
    '''User's Hotel matches the Requesting User's Hotel.'''

    def has_object_permission(self, request, view, obj):
        return obj.profile.hotel == request.user.profile.hotel


class IsHotelOfUser(permissions.BasePermission):
    '''The Hotel Obj. is the User's Hotel.'''

    def has_object_permission(self, request, view, obj):
        return obj == request.user.profile.hotel
