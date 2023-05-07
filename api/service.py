from .models import Friendship, UserApplication
from django.contrib.auth.models import User
from rest_framework.response import Response


class FriendshipStatusHandler:
    result_messages = {
        "friendship": "friendship",
        "outcoming_application": "outcoming_application",
        "incoming_application": "incoming_application",
        "no_friendship": "no_friendship"
    }

    def friendship_status(self, username1: str, username2: str) -> str:
        username1 = User.objects.get(username=username1)
        username2 = User.objects.get(username=username2)
        # Если есть дружба - возвращаем статус "Дружба"
        if self.is_friendship(username1, username2):
            return self.result_messages["friendship"]
        # Иначе если ищем заявки
        elif self.is_application(username1, username2):
            return self.application_status(username1, username2)
        # Иначе возвращаем, что дружбы нет
        else:
            return self.result_messages["no_friendship"]

    @staticmethod
    def is_friendship(username1: User, username2: User) -> bool:
        return Friendship.objects.filter(user1=username1, user2=username2).exists() or Friendship.objects.filter(
            user1=username2, user2=username1).exists()

    @staticmethod
    def is_application(username1: User, username2: User) -> bool:
        return UserApplication.objects.filter(user_from=username1, user_to=username2,
                                              status="Отправлена").exists() or UserApplication.objects.filter(
            user_from=username2, user_to=username1, status="Отправлена").exists()

    def application_status(self, username1: User, username2: User) -> str:
        outcoming_model = UserApplication.objects.filter(user_from=username1, user_to=username2, status="Отправлена")
        incoming_model = UserApplication.objects.filter(user_from=username2, user_to=username1, status="Отправлена")
        if outcoming_model.exists():
            return self.result_messages["outcoming_application"]
        elif incoming_model.exists():
            return self.result_messages["incoming_application"]
        else:
            return self.result_messages["no_friendship"]


def filter_queryset(user):
    queryset = UserApplication.objects.all().order_by('created_at').filter(user_from=user, status="Отправлена")
    sorted_accepted = UserApplication.objects.all().order_by('-created_at')
    queryset = queryset | sorted_accepted.filter(user_from=user, status="Принята")[:20]
    sorted_rejected = UserApplication.objects.all().order_by('-created_at')
    queryset = queryset | sorted_rejected.filter(user_from=user, status="Отклонена")[:20]
    return queryset


def is_there_incoming_application(username1, username2):
    return UserApplication.objects.filter(user_from=username2, user_to=username1,
                                          status="Отправлена").exists()


def user_application_create(self, serializer, request):
    validate_data = serializer.is_valid(raise_exception=True)
    if is_there_incoming_application(request.user, validate_data.get("user_to")):
        my_model = serializer.save()
        my_model.user_from = request.user
        my_model.status = "Отправлена"
        my_model.save()
    else:
        create_friendship(request.user, validate_data.get("user_to"))
    headers = self.get_success_headers(serializer.data)
    return Response(serializer.data, status=201, headers=headers)


def create_friendship(username1, username2):
    if FriendshipStatusHandler.is_friendship(username1, username2):
        raise Exception("Пользователь уже у вас в друзьях")
    username1 = User.objects.get(username1)
    username2 = User.objects.get(username2)
    Friendship.objects.create(user1=username1, user2=username2)

