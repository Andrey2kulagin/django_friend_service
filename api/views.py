from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserIncomingApplicationSerializer, ApplicationSerializer, \
    ApplicationSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from .service import FriendshipStatusHandler, filter_queryset
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from .models import UserApplication


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_permissions(self):
        if self.action == 'update':
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        method = self.request.method
        queryset = User.objects.all()
        action = self.action
        if method == "GET" and action == 'list':
            search_string = self.request.query_params.get('searchString', None)
            if search_string:
                queryset = User.objects.filter(username__icontains=search_string)
            else:
                queryset = User.objects.all()

        if method == "PATCH" and action == 'update':
            queryset = User.objects.filter(username=self.request.user)
        return queryset


class FriendshipStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        try:
            friendship_status = FriendshipStatusHandler().friendship_status(self.request.user, username)
            data = {'friendship_status': friendship_status}
            return Response(data, status=200)
        except User.DoesNotExist:
            data = {'Error': "Не найден пользователь"}
            return Response(data, status=404)
        except Exception as e:
            data = {'Error': e.args[0]}
            return Response(data, status=400)


class IncomingApplicationsList(ListAPIView):
    queryset = UserApplication.objects.all()
    serializer_class = UserIncomingApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method == "GET":
            queryset = UserApplication.objects.filter(user_to=self.request.user, status="Отправлена").order_by(
                '-created_at')
        return queryset


class OutcomingApplicationsList(ListAPIView):
    queryset = UserApplication.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method == "GET":
            queryset = UserApplication.objects.filter(user_from=self.request.user, status="Отправлена").order_by(
                '-created_at')
        return queryset


class SendApplication(CreateAPIView):
    serializer_class = ApplicationSerializer
    queryset = UserApplication.objects.all()
    permission_classes = [IsAuthenticated]
