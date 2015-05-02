from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User, Group

from model_mommy import mommy

from account import helpers
from utils import create

class HelperTests(TestCase):

    def test_login_messages(self):
        assert isinstance(helpers.login_messages, dict)

    def test_salt(self):
        s = helpers.salt(10)
        assert isinstance(int(s), int)
        assert len(s) == 10

    def test_add_group(self):
        user = mommy.make(User)
        # creates a 'hotel_admin' Group
        create._get_groups_and_perms()
        
        # call function and confirm User is part of that group
        user = helpers.add_group(user=user, group='hotel_admin')
        
        assert User.objects.get(groups__name='hotel_admin')