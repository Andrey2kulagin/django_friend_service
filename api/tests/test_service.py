import django.db
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from ..models import UserApplication, Friendship
from ..service import FriendshipStatusHandler
from django.core.exceptions import ObjectDoesNotExist

class FriendshipStatusHandlerTest(TestCase):
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
        UserApplication.objects.create(user_from=self.first_user, user_to=self.second_user, status="Отправлена", )
        UserApplication.objects.create(user_from=self.second_user, user_to=self.third_user, status="Принята", )
        UserApplication.objects.create(user_from=self.third_user, user_to=self.fourth_user, status="Отклонена", )
        Friendship.objects.create(user1=self.second_user, user2=self.third_user)

    def test_is_friendship_1(self):
        # Тест не дружбы
        self.assertEqual(False, FriendshipStatusHandler.is_friendship(self.first_user, self.second_user))

    def test_is_friendship_2(self):
        # Тест дружбы
        self.assertEqual(True, FriendshipStatusHandler.is_friendship(self.second_user, self.third_user))

    def test_is_application_1(self):
        # Исходящая заявка
        self.assertEqual(True, FriendshipStatusHandler.is_application(self.first_user, self.second_user))

    def test_is_application_2(self):
        # Входящая заявка
        self.assertEqual(True, FriendshipStatusHandler.is_application(self.second_user, self.first_user))

    def test_is_application_3(self):
        # Нет заявки
        self.assertEqual(False, FriendshipStatusHandler.is_application(self.fourth_user, self.first_user))

    def test_is_application_4(self):
        # Есть отклоненная заявка = нет заявки
        self.assertEqual(False, FriendshipStatusHandler.is_application(self.third_user, self.fourth_user))

    def test_is_application_5(self):
        # Есть принятая заявка = нет заявки
        self.assertEqual(False, FriendshipStatusHandler.is_application(self.second_user, self.third_user))

    def test_application_status_1(self):
        # Исходящая заявка
        self.assertEqual(FriendshipStatusHandler.result_messages["outcoming_application"],
                         FriendshipStatusHandler().application_status(self.first_user, self.second_user))

    def test_application_status_2(self):
        # Входящая заявка
        self.assertEqual(FriendshipStatusHandler.result_messages["incoming_application"],
                         FriendshipStatusHandler().application_status(self.second_user, self.first_user))

    def test_application_status_3(self):
        # Нет заявки
        self.assertEqual(FriendshipStatusHandler.result_messages["no_friendship"],
                         FriendshipStatusHandler().application_status(self.fourth_user, self.first_user))

    def test_application_status_4(self):
        # Есть отклоненная заявка = нет заявки
        self.assertEqual(FriendshipStatusHandler.result_messages["no_friendship"],
                         FriendshipStatusHandler().application_status(self.third_user, self.fourth_user))

    def test_application_status_5(self):
        # Есть принятая заявка = нет заявки
        self.assertEqual(FriendshipStatusHandler.result_messages["no_friendship"],
                         FriendshipStatusHandler().application_status(self.second_user, self.third_user))

    def test_friendship_status_1(self):
        # Дружба
        self.assertEqual(FriendshipStatusHandler.result_messages["friendship"],
                         FriendshipStatusHandler().friendship_status(self.second_user, self.third_user))

    def test_friendship_status_2(self):
        # Исходящая заявка
        self.assertEqual(FriendshipStatusHandler.result_messages["outcoming_application"],
                         FriendshipStatusHandler().friendship_status(self.first_user, self.second_user))

    def test_friendship_status_3(self):
        # Входящая заявка
        self.assertEqual(FriendshipStatusHandler.result_messages["incoming_application"],
                         FriendshipStatusHandler().friendship_status(self.second_user, self.first_user))

    def test_friendship_status_4(self):
        # Нет заявки
        self.assertEqual(FriendshipStatusHandler.result_messages["no_friendship"],
                         FriendshipStatusHandler().friendship_status(self.fourth_user, self.first_user))

    def test_friendship_status_5(self):
        # Есть отклоненная заявка = нет заявки
        self.assertEqual(FriendshipStatusHandler.result_messages["no_friendship"],
                         FriendshipStatusHandler().friendship_status(self.third_user, self.fourth_user))

    def test_friendship_status_6(self):
        # Нет пользоавателя, по которому ищут информацию
        self.assertRaises(ObjectDoesNotExist, FriendshipStatusHandler().friendship_status, "third_user", "no_username")

