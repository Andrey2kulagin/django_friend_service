from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import UserApplication, Friendship
from ..service import FriendshipStatusHandler


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
        self.assertEqual(len(User.objects.all()), len(response.data))


class UserUpdateTest(APITestCase):
    def setUp(self):
        # создаем пользователя
        self.first_user = User.objects.create_user(
            username='first_user', password='password')
        self.second_user = User.objects.create_user(
            username='second_user', password='password')

    def test_user_update_1(self):
        # тест без авторизации
        url = reverse('user_update', kwargs={'username': self.first_user.username})
        data = {
            "username": 'first',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(401, response.status_code)

    def test_user_update_2(self):
        # тест изменение username
        url = reverse('user_update', kwargs={'username': self.first_user.username})
        data = {
            "username": 'first',
        }
        self.client.force_authenticate(user=self.first_user)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(User.objects.filter(username="first")))
        user = User.objects.get(username="first")
        self.assertEqual(user.username, response.data["username"])
        self.assertEqual(user.id, response.data["id"])

    def test_user_update_3(self):
        # тест изменение username на тот, который уже есть
        url = reverse('user_update', kwargs={'username': self.first_user.username})
        data = {
            "username": 'second_user',
        }
        self.client.force_authenticate(user=self.first_user)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_user_update_4(self):
        # тест изменение только пароля
        url = reverse('user_update', kwargs={'username': self.first_user.username})
        data = {
            "password": 'first',
        }
        self.client.force_authenticate(user=self.first_user)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_user_update_5(self):
        # тест c расзыми паролем и confirm
        url = reverse('user_update', kwargs={'username': self.first_user.username})
        data = {
            "password": 'first',
            "confirm_password": 'first1',
        }
        self.client.force_authenticate(user=self.first_user)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_user_update_6(self):
        # изменение не своих данных
        url = reverse('user_update', kwargs={'username': self.second_user.username})
        data = {
            "password": 'first',
            "confirm_password": 'first',
        }
        self.client.force_authenticate(user=self.first_user)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(404, response.status_code)

    def test_user_update_7(self):
        # Изменение пароля
        url = reverse('user_update', kwargs={'username': self.first_user.username})
        data = {
            "password": 'first',
            "confirm_password": 'first',
        }
        self.client.force_authenticate(user=self.first_user)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(200, response.status_code)


class UserDetailTest(APITestCase):
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

    def test_user_detail_1(self):
        # стандартная работа
        url = reverse('user_detail', kwargs={'username': self.first_user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.first_user.username, response.data["username"])
        self.assertEqual(self.first_user.id, response.data["id"])

    def test_user_detail_2(self):
        # Показ пользователя, которого нет
        url = reverse('user_detail', kwargs={'username': "no_username"})
        response = self.client.get(url, format='json')
        self.assertEqual(404, response.status_code)


class UserDeleteTest(APITestCase):
    def setUp(self):
        # создаем 4 пользователей
        self.first_user = User.objects.create_user(
            username='first_user', password='password')

    def test_user_delete_1(self):
        # стандартная работа
        self.client.force_authenticate(user=self.first_user)
        url = reverse('user_delete', kwargs={'username': self.first_user.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(204, response.status_code)
        self.assertEqual(0, len(User.objects.filter(username=self.first_user.username)))

    def test_user_delete_2(self):
        # Удаление не своего аккаунта
        url = reverse('user_delete', kwargs={'username': "no_username"})
        self.client.force_authenticate(user=self.first_user)
        response = self.client.delete(url, format='json')
        self.assertEqual(404, response.status_code)

    def test_user_delete_3(self):
        # Удаление без авторизации
        url = reverse('user_delete', kwargs={'username': "no_username"})
        response = self.client.delete(url, format='json')
        self.assertEqual(401, response.status_code)


class UserFriendshipStatusTest(APITestCase):
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
        UserApplication.objects.create(user_from=self.second_user, user_to=self.third_user, status="Принята", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.fourth_user, status="Отклонена", )
        # Создаем дружбу
        Friendship.objects.create(user1=self.second_user, user2=self.third_user)

    def test_friendship_status_1(self):
        # дружба
        self.client.force_authenticate(user=self.second_user)
        url = reverse('is_friend', kwargs={'username': self.third_user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(FriendshipStatusHandler.result_messages["friendship"], response.data["friendship_status"])

    def test_friendship_status_2(self):
        # не авторизован
        url = reverse('is_friend', kwargs={'username': self.third_user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(401, response.status_code)

    def test_friendship_status_3(self):
        # нет ничего
        self.client.force_authenticate(user=self.third_user)
        url = reverse('is_friend', kwargs={'username': self.first_user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(FriendshipStatusHandler.result_messages["no_friendship"], response.data["friendship_status"])

    def test_friendship_status_4(self):
        # Исходящая заявка
        self.client.force_authenticate(user=self.first_user)
        url = reverse('is_friend', kwargs={'username': self.second_user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(FriendshipStatusHandler.result_messages["outcoming_application"],
                         response.data["friendship_status"])

    def test_friendship_status_5(self):
        # Входящая заявка
        self.client.force_authenticate(user=self.second_user)
        url = reverse('is_friend', kwargs={'username': self.first_user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(FriendshipStatusHandler.result_messages["incoming_application"],
                         response.data["friendship_status"])

    def test_friendship_status_6(self):
        # Отказ =  нет заявки
        self.client.force_authenticate(user=self.third_user)
        url = reverse('is_friend', kwargs={'username': self.fourth_user.username})
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(FriendshipStatusHandler.result_messages["no_friendship"],
                         response.data["friendship_status"])

    def test_friendship_status_7(self):
        # Нет пользователя, по которому ищется информация
        self.client.force_authenticate(user=self.third_user)
        url = reverse('is_friend', kwargs={'username': "No user"})
        response = self.client.get(url, format='json')
        self.assertEqual(404, response.status_code)

