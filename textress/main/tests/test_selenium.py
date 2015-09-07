# import time

# from django.test import LiveServerTestCase
# from django.conf import settings
# from django.core.urlresolvers import reverse
# from django.core.exceptions import ValidationError
# from django.contrib.auth.models import User, Group

# import stripe

# from selenium.webdriver.firefox.webdriver import WebDriver
# from selenium.webdriver.common.keys import Keys

# from main.models import Hotel, UserProfile, Subaccount
# from main.tests.factory import (CREATE_USER_DICT, CREATE_HOTEL_DICT,
#     create_hotel, create_hotel_user)
# from utils import create
# from utils.messages import dj_messages


# stripe.api_key = settings.STRIPE_SECRET_KEY


# class SeleniumTests(LiveServerTestCase):

#     @classmethod
#     def setUpClass(cls):
#         super(SeleniumTests, cls).setUpClass()
#         cls.selenium = WebDriver()
#         cls.selenium.set_window_size(1200, 800)

#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super(SeleniumTests, cls).tearDownClass()

#     def test_registration_step1(self):
#         self.selenium.get('%s%s' % (self.live_server_url, '/register/step1/'))
#         username_input = self.selenium.find_element_by_name("first_name")
#         username_input.send_keys(CREATE_USER_DICT["first_name"])
#         username_input = self.selenium.find_element_by_name("last_name")
#         username_input.send_keys(CREATE_USER_DICT["last_name"])
#         username_input = self.selenium.find_element_by_name("email")
#         username_input.send_keys(CREATE_USER_DICT["email"])
#         username_input = self.selenium.find_element_by_name("username")
#         username_input.send_keys(CREATE_USER_DICT["username"])
#         username_input = self.selenium.find_element_by_name("password1")
#         username_input.send_keys(CREATE_USER_DICT["password1"])
#         username_input = self.selenium.find_element_by_name("password2")
#         username_input.send_keys(CREATE_USER_DICT["password2"])
#         self.selenium.execute_script("window.scrollBy(0, 250);")
#         time.sleep(1)
#         username_input.send_keys(Keys.RETURN)
#         time.sleep(3)



