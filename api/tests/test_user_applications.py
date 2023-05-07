from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import UserApplication, Friendship


class InOutcomingApplicationsTest(APITestCase):
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
        # Создаем заявки
        UserApplication.objects.create(user_from=self.first_user, user_to=self.second_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.second_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.first_user, user_to=self.third_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.second_user, user_to=self.third_user, status="Принята", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.fourth_user, status="Отклонена", )

    def test_incoming_list_1(self):
        # стандартная работа
        url = reverse('incoming_list')
        self.client.force_authenticate(user=self.second_user)
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.data))

    def test_incoming_list_2(self):
        # отсутствие заявок
        url = reverse('incoming_list')
        self.client.force_authenticate(user=self.first_user)
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_incoming_list_3(self):
        # неавторизованный юзер
        url = reverse('incoming_list')
        response = self.client.get(url, format='json')
        self.assertEqual(401, response.status_code)

    def test_outcoming_list_1(self):
        # стандартная работа
        url = reverse('outcoming_list')
        self.client.force_authenticate(user=self.third_user)
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.data))

    def test_outcoming_list_2(self):
        # отсутствие заявок
        url = reverse('outcoming_list')
        self.client.force_authenticate(user=self.fourth_user)
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_outcoming_list_3(self):
        # неавторизованный юзер
        url = reverse('outcoming_list')
        response = self.client.get(url, format='json')
        self.assertEqual(401, response.status_code)


class SendApplicationsTest(APITestCase):
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

    def test_send_application_1(self):
        # стандартная работа
        url = reverse('send_application')
        data = {
            "user_to": self.first_user.username
        }
        self.client.force_authenticate(user=self.second_user)
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.data))
