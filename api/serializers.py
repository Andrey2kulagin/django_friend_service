from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserApplication


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
    class Meta:
        model = UserApplication
        fields = [
            "user_from"
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApplication
        fields = [
            "user_to",
            "status"
        ]

    def get_fields(self):
        fields = super().get_fields()
        if self.context.get('requests').method == "POST":
            fields["status"].required = False
