from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import UserApplication, Friendship


class FriendListDeleteTest(APITestCase):
    def setUp(self):
        # создаем пользователей
        self.first_user = User.objects.create_user(
            username='first_user', password='password')
        self.second_user = User.objects.create_user(
            username='second_user', password='password')
        self.third_user = User.objects.create_user(
            username='third_user', password='password')
        self.fourth_user = User.objects.create_user(
            username='fourth_user', password='password')
        self.fifth_user = User.objects.create_user(
            username='fifth_user', password='password')
        self.sixth_user = User.objects.create_user(
            username='sixth_user', password='password')
        self.seventh = User.objects.create_user(
            username='seventh', password='password')
        # Создаем друзей
        self.friendship1 = Friendship.objects.create(user1=self.first_user, user2=self.second_user)
        Friendship.objects.create(user1=self.first_user, user2=self.third_user)
        Friendship.objects.create(user1=self.first_user, user2=self.fourth_user)
        Friendship.objects.create(user1=self.first_user, user2=self.fifth_user)
        Friendship.objects.create(user1=self.first_user, user2=self.sixth_user)

    def test_incoming_list_1(self):
        # стандартная работа
        url = reverse('friends_list')
        self.client.force_authenticate(user=self.first_user)
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.data))
        self.assertEqual(self.friendship1.user2.id, response.data[0]["id"])
        self.assertEqual(self.friendship1.user2.username, response.data[0]["username"])

    def test_incoming_list_2(self):
        # нет друзей
        url = reverse('friends_list')
        self.client.force_authenticate(user=self.seventh)
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_incoming_list_3(self):
        # не авторизован
        url = reverse('friends_list')
        response = self.client.get(url, format='json')
        self.assertEqual(401, response.status_code)

    def test_incoming_delete_1(self):
        # стандартная работа
        url = reverse('friends_delete',  kwargs={'username': self.second_user.username})
        self.client.force_authenticate(user=self.first_user)
        response = self.client.delete(url, format='json')
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(Friendship.objects.filter(user1=self.first_user, user2=self.second_user)))

    def test_incoming_delete_2(self):
        # Нет дружбы с удаляемым юзером
        url = reverse('friends_delete',  kwargs={'username': self.seventh.username})
        self.client.force_authenticate(user=self.first_user)
        response = self.client.delete(url, format='json')
        self.assertEqual(400, response.status_code)

    def test_incoming_delete_3(self):
        # Нет юзера
        url = reverse('friends_delete',  kwargs={'username': "NoUser"})
        self.client.force_authenticate(user=self.first_user)
        response = self.client.delete(url, format='json')
        self.assertEqual(404, response.status_code)
