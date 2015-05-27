import random
import stripe
from model_mommy import mommy

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from main.models import Hotel, UserProfile
from concierge.models import Guest, Message


LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

def random_lorem(words=5):
    msg = []
    for w in range(words):
        msg.append(random.choice(LOREM_IPSUM.split()))
    return ' '.join(msg)



#############################
# USER PERMISSIONS / GROUPS #
#############################

# Use for each Group / Permission naming
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


#########
# USERS #
#########
def _get_users():
    """
    Will create 15 Users. 5 of ea. Group.
    """
    groups = ['hotel_admin', 'hotel_manager', '']
    for group in groups:
        for i in range(5):
            try:
                user = User.objects.get(username="User{}_{}".format(str(i),group))
            except ObjectDoesNotExist:
                user = mommy.make(User,
                    username="User{}_{}".format(str(i),group),
                    password="1234")
                if group:
                    g, created = Group.objects.get_or_create(name=group)
                    user.groups.add(g)
                    user.save()
    # make sure PW is set
    users = User.objects.all()
    for u in users:
        u.set_password('1234')
        u.save()
    return User.objects.filter(~Q(username="Test"))


##########
# HOTELS #
##########  
def _generate_ph():
    n = ''
    for i in range(10):
        n += str(random.randrange(0,10))
    return n

def _get_hotels():
    """Get ALL None 'Test' Hotels."""
    for i in range(5):
        try:
            hotel = Hotel.objects.get(name="Hotel{}".format(str(i)))
        except ObjectDoesNotExist:
            mommy.make(Hotel,
                name="Hotel{}".format(str(i)),
                address_phone=_generate_ph(),
                twilio_phone_number=_generate_ph(),
                twilio_sid=random.randrange(1,999),
                twilio_ph_sid=random.randrange(1,999))
    return Hotel.objects.filter(~Q(name="Test"))

def _phone_numbers():
    """
    settings.DEFAULT_TO_PH == +17026018602
    Adds #'s ending in 3,4,5 
    """
    phone_numbers = [settings.DEFAULT_TO_PH, settings.DEFAULT_TO_PH_2]
    for i in range(3):
        phone_numbers.append("+1702601860"+str(int(settings.DEFAULT_TO_PH[-1])+i+3))
    return phone_numbers 


##########
# GUESTS #
##########   
def _get_guests():
    hotels = Hotel.objects.all()
    phone_numbers = _phone_numbers()
    for i in range(5):
        mommy.make(Guest,
            name="Guest{}".format(str(i)),
            hotel=hotels[i],
            phone_number=phone_numbers[i])
    return Guest.objects.all() 


########
# MAIN #
######## 
def create_main():
    """
    15 Users
    5 Hotels
    2 User Groups
    1 of ea. type p/Hotel
    5 Guests, 1 in ea. Hotel
    """
    users = _get_users()
    hotels = _get_hotels()
    guests = _get_guests()
    groups = ['hotel_admin', 'hotel_manager', None]

    for group in groups:
        n = 0
        for i in range(5):
            userprofile = UserProfile.objects.get(user=users[i+n])
            userprofile.update_hotel(hotels[i])
            n += 1

    for i in range(5):
        for x in range(5):
            if x % 2:
                mommy.make(Message,
                    guest=guests[i],
                    body=random_lorem())
            else:
                mommy.make(Message,
                    user=users[i],
                    body=random_lorem())

def clean_hotels():
    "Line up Hotel # w/ User #"
    users = _get_users()
    hotels = _get_hotels()
    for u in users:
        for h in hotels:
            if u.username[4] == h.name[5]:
                user_profile = u.profile
                user_profile.update_hotel(h)

    # delete blank username 'user'
    users = User.objects.filter(username='')
    [u.delete() for u in users]



def remove_all():
    models = [User, Group, Permission, UserProfile, Hotel, Guest, Message]
    for m in models:
        objs = m.objects.all()
        for o in objs:
            o.delete()

def clean_userprofiles():
    """Initial create_superuser doesn't create a UserProfile, so manually remove_all
    here, and re-add in final step."""
    users = User.objects.all()
    for u in users:
        if not u.profile:
            UserProfile.objects.create(user=u)


def superuser_profile():
    """"Make sure that all Users have a UserProfile. UserProfile's are not
    created during the "syncdb" command for some reason.
    """
    hotel, hotel_created = Hotel.objects.get_or_create(name="Test")
    su = User.objects.create(username="Aaron", email="pyaaron@gmail.com",
        password="1234", is_superuser=True, is_staff=True)
    su.set_password('1234')
    su.save()
    user_profile = UserProfile.objects.get(user=su)
    user_profile.update_hotel(hotel)


def create_all():
    "Regenerate all test records."
    clean_userprofiles()
    sites = Site.objects.all()
    if not sites:
        Site.objects.create(name=settings.SITE, domain=settings.SITE)
    remove_all()
    create_main()
    superuser_profile()
    clean_hotels()


if __name__ == '__main__':
    create_all()


