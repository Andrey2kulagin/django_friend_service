from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class UserCreateTest(APITestCase):

    def test_user_create_1(self):
        # Стандартное создание
        url = reverse('user_create')
        data = {
            'username': "username123",
            'password': "qwer123qw",
            'confirm_password': "qwer123qw"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(1, len(User.objects.all()))

    def test_user_create_2(self):
        # Без "confirm password"
        url = reverse('user_create')
        data = {
            'username': "username123",
            'password': "qwer123qw",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)
        self.assertEqual(0, len(User.objects.all()))

    def test_user_create_3(self):
        # разные пароли
        url = reverse('user_create')
        data = {
            'username': "username123",
            'password': "qwer13qw",
            'confirm_password': "qwer123qw"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)
        self.assertEqual(0, len(User.objects.all()))

    def test_user_create_4(self):
        # Пользователь уже существует
        url = reverse('user_create')
        data = {
            'username': "username123",
            'password': "qwer123qw",
            'confirm_password': "qwer123qw"
        }
        self.client.post(url, data, format='json')
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)
        self.assertEqual(1, len(User.objects.all()))


class UserListTest(APITestCase):
    def setUp(self):
        # создаем 4 пользователей
        self.first_user = User.objects.create_user(
            username='first_user', password='password')
        self.second_user = User.objects.create_user(
            username='second_user', password='password')
        self.third_user = User.objects.create_user(
            username='third_user', password='password')
        self.fourth_user = User.objects.create_user(
            username='fourth_user', password='password')

    def test_user_list_1(self):
        # лист 1 юзера с поисковым запросом
        url = reverse('user_list')
        data = {
            "searchString": 'first',
        }
        response = self.client.get(url, data, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual("first_user", response.data[0]["username"])
        self.assertEqual(1, len(response.data))

    def test_user_list_2(self):
        # лист всех пользователей
        url = reverse('user_list')
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(User.objects.all()), len(response.data))

    def test_user_list_3(self):
        # лист нескольких юзеров с поисковым запросом
        url = reverse('user_list')
        data = {
            "searchString": 'd',
        }
        response = self.client.get(url, data, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.data))

    def test_user_list_4(self):
        # лист юзеров при поисковом запросе, котороего нет
        url = reverse('user_list')
        data = {
            "searchString": '1',
        }
        response = self.client.get(url, data, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_user_list_5(self):
        # лист юзеров при пустом поисковом запросе
        url = reverse('user_list')
        data = {
            "searchString": '',
        }
        response = self.client.get(url, data, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(User.objects.all(), len(response.data))


'''
    def setUp(self):
        # создаем 2 пользователей
        self.first_user = User.objects.create_user(
            username='testuser', email='testuser@mail.com', password='password')
        self.first_token = Token.objects.create(user=self.user)
        self.first_token.save()
        self.second_user = User.objects.create_user(
            username='seconduser', email='testur@mail.com', password='password')
        self.second_token = Token.objects.create(user=self.second_user)
        self.second_token.save()
'''
