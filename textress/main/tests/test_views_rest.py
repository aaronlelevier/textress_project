import json

from django.contrib.auth.models import User
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

    def test_list__data(self):
        self.client.login(username=self.admin.username, password=self.password)
        
        response = self.client.get(reverse('main:api_users'), format='json')
        data = json.loads(response.content)
        
        data_user = data[0]
        user = User.objects.get(id=data_user['id'])
        self.assertEqual(data_user['username'], user.username)
        self.assertEqual(data_user['email'], user.email)
        self.assertEqual(data_user['first_name'], user.first_name)
        self.assertEqual(data_user['last_name'], user.last_name)
        self.assertIn('profile', data_user)
        self.assertEqual(data_user['profile']['icon'], user.profile.icon)
        self.assertEqual(data_user['profile']['hotel_group'], user.profile.hotel_group())

    def test_list__login(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('main:api_users'))
        self.assertEqual(response.status_code, 200)

    def test_list__logout(self):
        ## permissions.IsAuthenticated
        response = self.client.get(reverse('main:api_users'))
        self.assertEqual(response.status_code, 403)

    def test_list__normal_user(self):
        ## IsManagerOrAdmin
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:api_users'))
        self.assertEqual(response.status_code, 403)

    ### UserRetrieveAPIView ###

    def test_retrieve__data(self):
        self.client.login(username=self.admin.username, password=self.password)
        
        response = self.client.get(reverse('main:api_users', kwargs={'pk':self.user.pk}), format='json')
        data = json.loads(response.content)
        
        self.assertEqual(data['id'], self.user.id)
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['icon'], self.user.profile.icon)
        self.assertEqual(data['profile']['hotel_group'], self.user.profile.hotel_group())
        
    def test_retrieve__login(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('main:api_users', kwargs={'pk':self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_retrieve__other_hotel_user(self):
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

    def test_retrieve__data(self):
        self.client.login(username=self.admin_a.username, password=self.password)

        response = self.client.get(reverse('main:api_hotel', kwargs={'pk':self.hotel_a.pk}), format='json')
        data = json.loads(response.content)

        self.assertEqual(data['id'], self.hotel_a.id)
        self.assertEqual(data['name'], self.hotel_a.name)
        self.assertEqual(data['address_phone'], self.hotel_a.address_phone)
        self.assertEqual(data['address_line1'], self.hotel_a.address_line1)

    def test_retrieve__ok(self):
        self.client.login(username=self.admin_a.username, password=self.password)
        response = self.client.get(reverse('main:api_hotel', kwargs={'pk':self.hotel_a.pk}))
        self.assertEqual(response.status_code, 200)
