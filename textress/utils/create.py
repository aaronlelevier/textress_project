import random
import string

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from model_mommy import mommy

from main.models import Hotel, UserProfile
from concierge.models import Guest, Message


### LOREM

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

def random_lorem(words=5):
    msg = []
    for w in range(words):
        msg.append(random.choice(LOREM_IPSUM.split()))
    return ' '.join(msg)


### GROUPS

GROUPS = ['hotel_admin', 'hotel_manager']

def _get_groups_and_perms():
    "contenttypes and sites must be added to installed_apps to use."
    ct = ContentType.objects.get(app_label='main', model='userprofile')

    groups = ['hotel_admin', 'hotel_manager']
    for ea in groups:
        group = Group.objects.create(name=ea)
        perm = Permission.objects.create(name=ea, codename="is_"+ea, content_type=ct)
        group.permissions.add(perm)
        group.save()


### GENERATORS

def _generate_ph(numbers=10):
    return ''.join([random.choice(string.digits) for x in range(numbers)])


def _generate_name(letters=10):
    return ''.join([random.choice(string.ascii_letters) for x in range(letters)])


def _phone_numbers():
    """
    settings.DEFAULT_TO_PH == +17026018602
    Adds #'s ending in 3,4,5 
    """
    phone_numbers = []
    for i in range(5):
        phone_numbers.append("+1702601860"+str(int(settings.DEFAULT_TO_PH[-1])+i+3))
    return phone_numbers