from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from ..models import UserApplication, Friendship


class InOutcomingApplicationsTest(APITestCase):
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
        # Создаем заявки
        UserApplication.objects.create(user_from=self.first_user, user_to=self.second_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.fifth_user, user_to=self.second_user, status="Принята", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.second_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.first_user, user_to=self.third_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.second_user, user_to=self.third_user, status="Принята", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.fourth_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.fifth_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.sixth_user, status="Отклонена", )

    def test_incoming_list_1(self):
        # стандартная работа
        url = reverse('incoming_list')
        self.client.force_authenticate(user=self.second_user)
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.data))
        incoming_applications = UserApplication.objects.filter(user_to=self.second_user, status="Отправлена").order_by(
            '-created_at')
        self.assertEqual(incoming_applications[0].user_from.username, response.data[0]["user_from"])
        self.assertEqual(incoming_applications[1].user_from.username, response.data[1]["user_from"])

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
        outcoming_applications = UserApplication.objects.filter(user_from=self.third_user,
                                                                status="Отправлена").order_by('-created_at')
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response.data))
        self.assertEqual(outcoming_applications[0].user_to.username, response.data[0]["user_to"])
        self.assertEqual(outcoming_applications[0].status, response.data[0]["status"])
        self.assertEqual(outcoming_applications[1].user_to.username, response.data[1]["user_to"])
        self.assertEqual(outcoming_applications[1].status, response.data[1]["status"])
        self.assertEqual(outcoming_applications[2].user_to.username, response.data[2]["user_to"])
        self.assertEqual(outcoming_applications[2].status, response.data[1]["status"])

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
        # создаем пользователей
        self.first_user = User.objects.create_user(
            username='first_user', password='password')
        self.second_user = User.objects.create_user(
            username='second_user', password='password')
        self.third_user = User.objects.create_user(
            username='third_user', password='password')
        self.fourth_user = User.objects.create_user(
            username='fourth_user', password='password')
        self.application = UserApplication.objects.create(user_from=self.third_user, user_to=self.second_user,
                                                          status="Отправлена", )
        Friendship.objects.create(user1=self.fourth_user, user2=self.first_user)

    def test_send_application_1(self):
        # стандартная работа
        url = reverse('send_application')
        data = {
            "user_to": self.first_user.username
        }
        self.client.force_authenticate(user=self.second_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(201, response.status_code)
        application = UserApplication.objects.get(user_from=self.second_user, user_to=self.first_user)
        self.assertEqual("Отправлена", application.status)

    def test_send_application_2(self):
        # Пользователя с таким именем не существует
        url = reverse('send_application')
        data = {
            "user_to": "no_username"
        }
        self.client.force_authenticate(user=self.second_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_send_application_3(self):
        # Заявка уже отправлена
        url = reverse('send_application')
        data = {
            "user_to": self.second_user.username
        }
        self.client.force_authenticate(user=self.third_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_send_application_4(self):
        # заявка, переходящая в дружбу
        url = reverse('send_application')
        data = {
            "user_to": self.third_user.username
        }
        self.client.force_authenticate(user=self.second_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(201, response.status_code)
        application = UserApplication.objects.get(user_from=self.third_user, user_to=self.second_user)
        self.assertEqual("Принята", application.status)
        self.assertEqual(1, len(Friendship.objects.filter(user1=self.second_user, user2=self.third_user)))

    def test_send_application_5(self):
        # заявка другу
        url = reverse('send_application')
        data = {
            "user_to": self.fourth_user.username
        }
        self.client.force_authenticate(user=self.first_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)


class DeleteApplicationsTest(APITestCase):
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
        # Создаем заявки
        UserApplication.objects.create(user_from=self.first_user, user_to=self.second_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.fifth_user, user_to=self.second_user, status="Принята", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.second_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.first_user, user_to=self.third_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.second_user, user_to=self.third_user, status="Принята", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.fourth_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.fifth_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.sixth_user, status="Отклонена", )

    def test_delete_application_1(self):
        # стандартная работа
        url = reverse('delete_application', kwargs={'user_to_username': self.fifth_user.username})
        self.client.force_authenticate(user=self.third_user)
        response = self.client.delete(url, format='json')
        self.assertEqual(204, response.status_code)
        application = UserApplication.objects.filter(user_from=self.third_user, user_to=self.fifth_user)
        self.assertEqual(0, len(application))

    def test_delete_application_2(self):
        # Удаление заявки, которой нет
        url = reverse('delete_application', kwargs={'user_to_username': self.first_user.username})
        self.client.force_authenticate(user=self.third_user)
        response = self.client.delete(url, format='json')
        self.assertEqual(404, response.status_code)

    def test_delete_application_3(self):
        # Удаление заявки, без авторизации
        url = reverse('delete_application', kwargs={'user_to_username': self.fifth_user.username})
        response = self.client.delete(url, format='json')
        self.assertEqual(401, response.status_code)

    def test_delete_application_4(self):
        # Удаление по username, которого нет
        url = reverse('delete_application', kwargs={'user_to_username': "NoUsername"})
        self.client.force_authenticate(user=self.third_user)
        response = self.client.delete(url, format='json')
        self.assertEqual(404, response.status_code)



class DecisionApplicationsTest(APITestCase):
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
        # Создаем заявки
        UserApplication.objects.create(user_from=self.first_user, user_to=self.second_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.fifth_user, user_to=self.second_user, status="Принята", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.second_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.first_user, user_to=self.third_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.second_user, user_to=self.third_user, status="Принята", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.fourth_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.fifth_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.sixth_user, status="Отклонена", )
        UserApplication.objects.create(user_from=self.first_user, user_to=self.fourth_user, status="Отправлена", )
        Friendship.objects.create(user1=self.fourth_user, user2=self.first_user)

    def test_delete_application_1(self):
        # стандартная работа Принять заявку
        user_from = self.first_user
        user_to = self.third_user
        url = reverse('decision')
        data = {
            'username': user_from.username,
            'decision': 'accepted'
        }
        self.client.force_authenticate(user=user_to)
        response = self.client.post(url, data, format='json')
        self.assertEqual(200, response.status_code)
        application = UserApplication.objects.get(user_from=user_from, user_to=user_to)
        self.assertEqual("Принята", application.status)
        friendship = Friendship.objects.filter(user1=user_to, user2=user_from)
        self.assertEqual(1, len(friendship))

    def test_delete_application_2(self):
        # стандартная работа Отклонить заявку
        user_from = self.first_user
        user_to = self.third_user
        url = reverse('decision')
        data = {
            'username': user_from.username,
            'decision': 'rejected'
        }
        self.client.force_authenticate(user=user_to)
        response = self.client.post(url, data, format='json')
        self.assertEqual(200, response.status_code)
        application = UserApplication.objects.get(user_from=user_from, user_to=user_to)
        self.assertEqual("Отклонена", application.status)
        friendship = Friendship.objects.filter(user1=user_to, user2=user_from)
        self.assertEqual(0, len(friendship))

    def test_delete_application_3(self):
        # Подтверждение несуществующей заявки
        user_from = self.sixth_user
        user_to = self.third_user
        url = reverse('decision')
        data = {
            'username': user_from.username,
            'decision': 'rejected'
        }
        self.client.force_authenticate(user=user_to)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_delete_application_4(self):
        # неправильный статус заявки
        user_from = self.first_user
        user_to = self.third_user
        url = reverse('decision')
        data = {
            'username': user_from.username,
            'decision': 'rejectded'
        }
        self.client.force_authenticate(user=user_to)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_delete_application_5(self):
        # Несуществующий юзер
        user_to = self.third_user
        url = reverse('decision')
        data = {
            'username': "No_user",
            'decision': 'rejected'
        }
        self.client.force_authenticate(user=user_to)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

    def test_delete_application_6(self):
        # Уже друзья
        url = reverse('decision')
        data = {
            'username': self.first_user.username,
            'decision': 'rejected'
        }
        self.client.force_authenticate(user=self.fourth_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(400, response.status_code)

