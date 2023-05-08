from abc import ABC

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserApplication, Friendship
from .service import is_there_incoming_application, create_friendship, set_application_status, \
    FriendshipStatusHandler


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=50, write_only=True, required=False)
    confirm_password = serializers.CharField(max_length=50, write_only=True, required=False)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "confirm_password"
        ]

    def validate(self, data):
        if "password" in data:
            if "confirm_password" in data:
                if data["password"] != data["confirm_password"]:
                    raise serializers.ValidationError("Пароли не совпадают")
            else:
                raise serializers.ValidationError("Подтвердите пароль")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        if "password" in validated_data:
            validated_data.pop("confirm_password")
        return super().update(instance, validated_data)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request.method == "POST":
            fields['username'].required = True
            fields['password'].required = True
            fields['confirm_password'].required = True
        if request.method == "PATCH":
            fields['username'].required = False
            fields['password'].required = False
            fields['confirm_password'].required = False
        return fields


class UserIncomingApplicationSerializer(serializers.ModelSerializer):
    user_from = serializers.CharField(source='user_from.username')

    class Meta:
        model = UserApplication
        fields = [
            "user_from"
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    user_to = serializers.CharField(source='user_to.username')

    class Meta:
        model = UserApplication
        fields = [
            "user_to",
            "status"
        ]

    def validate(self, data):
        user_to_username = data['user_to']["username"]
        users = User.objects.filter(username=user_to_username)
        request = self.context.get("request")
        if not users.exists():
            raise serializers.ValidationError("Пользователя с таким именем не существует")
        user_from_active_applications = UserApplication.objects.filter(user_from=request.user,
                                                                       user_to=users[0], status="Отправлена")
        if user_from_active_applications.exists():
            raise serializers.ValidationError("Уже есть активная заявка с этим пользователем")
        if FriendshipStatusHandler.is_friendship(request.user, users[0]):
            raise serializers.ValidationError("Уже дружба этим пользователем")
        return data

    def get_fields(self):
        fields = super().get_fields()
        if self.context.get('request').method == "POST":
            fields["status"].required = False
        return fields

    def create(self, validated_data):
        request = self.context.get("request")
        user_to_username = validated_data.pop('user_to')["username"]
        validated_data["user_to"] = User.objects.get(username=user_to_username)
        validated_data["user_from"] = request.user
        if not is_there_incoming_application(request.user.username, user_to_username):
            validated_data["status"] = "Отправлена"
        else:
            set_application_status(request.user.username, user_to_username, "Принята")
            create_friendship(request.user.username, user_to_username)
            validated_data["status"] = "Принята"
        return super().create(validated_data)


class DecisionSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    decision = serializers.CharField(max_length=100)

    def validate(self, data):
        if not data["decision"] in ["accepted", "rejected"]:
            raise serializers.ValidationError("decision должно быть accepted или rejected")
        to_users = User.objects.filter(username=data["username"])
        if not to_users.exists():
            raise serializers.ValidationError("Пользователя с таким именем нет")
        user_from = self.context.get('request').user
        if not UserApplication.objects.filter(user_from=to_users[0], user_to=user_from, status="Отправлена").exists():
            raise serializers.ValidationError("У вас нет активной заявки с этим пользователем")
        if FriendshipStatusHandler.is_friendship(user_from, to_users[0]):
            raise serializers.ValidationError("У вас уже есть дружба с этим пользователем")
        return data


class FriendshipSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = [
            'username',
            'id'
        ]

    def get_username(self, obj):
        if self.context['request'].user == obj.user1:
            return obj.user2.username
        else:
            return obj.user1.username

    def get_id(self, obj):
        if self.context['request'].user == obj.user1:
            return obj.user2.id
        else:
            return obj.user1.id
