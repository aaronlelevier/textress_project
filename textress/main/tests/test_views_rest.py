from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase

from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from utils import create


class UserAPIViewTests(APITestCase):

    def setUp(self):
        self.password = PASSWORD
        self.hotel = create_hotel()
        self.hotel_b = create_hotel(name='hotel_b')

        # create Groups
        create._get_groups_and_perms()

        # Users
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        self.mgr = create_hotel_user(hotel=self.hotel, username='mgr', group='hotel_manager')
        self.user = create_hotel_user(hotel=self.hotel, username='user1')
        self.admin_b = create_hotel_user(hotel=self.hotel_b, username='admin_b', group='hotel_admin')

    ### UserListAPIView ###
        
    def test_list_login(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('main:api_users'))
        self.assertEqual(response.status_code, 200)

    def test_list_logout(self):
        ## permissions.IsAuthenticated
        response = self.client.get(reverse('main:api_users'))
        self.assertEqual(response.status_code, 403)

    def test_list_normal_user(self):
        ## IsManagerOrAdmin
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:api_users'))
        self.assertEqual(response.status_code, 403)

    ### UserRetrieveAPIView ###
        
    def test_retrieve_login(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('main:api_users', kwargs={'pk':self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_retrieve_other_hotel_user(self):
        ## IsHotelUser
        self.client.login(username=self.admin_b.username, password=self.password)
        response = self.client.get(reverse('main:api_users', kwargs={'pk':self.user.pk}))
        self.assertEqual(response.status_code, 403)


class HotelAPIViewTests(APITestCase):

    def setUp(self):
        self.password = PASSWORD
        self.hotel_a = create_hotel(name='hotel_a')
        self.hotel_b = create_hotel(name='hotel_b')

        # create Groups
        create._get_groups_and_perms()

        # Users
        self.admin_a = create_hotel_user(hotel=self.hotel_a, username='admin_a', group='hotel_admin')
        self.admin_b = create_hotel_user(hotel=self.hotel_b, username='admin_b', group='hotel_admin')

    ### HotelRetrieveAPIView ###

    def test_retrieve_ok(self):
        self.client.login(username=self.admin_a.username, password=self.password)
        response = self.client.get(reverse('main:api_hotel', kwargs={'pk':self.hotel_a.pk}))
        self.assertEqual(response.status_code, 200)
