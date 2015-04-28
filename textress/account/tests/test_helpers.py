from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from model_mommy import mommy

from account.helpers import login_messages, salt, forgot_password_email


class HelperTests(TestCase):

    def setUp(self):
        self.user = mommy.make(User)

    def test_login_messages(self):
        assert isinstance(login_messages, dict)

    def test_salt(self):
        s = salt(10)
        assert isinstance(int(s), int)
        assert len(s) == 10

    def test_forgot_password_email(self):
        msg = forgot_password_email(
            username=self.user.username,
            email=settings.DEFAULT_FROM_EMAIL,
            temp_password=salt())
        assert msg