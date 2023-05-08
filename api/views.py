from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserIncomingApplicationSerializer, ApplicationSerializer, DecisionSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from .service import FriendshipStatusHandler, set_decision
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView
from .models import UserApplication
from django.shortcuts import get_object_or_404


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
            friendship_status = FriendshipStatusHandler().friendship_status(request.user, username)
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


class DeleteApplication(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'user_to__username'

    def get_queryset(self):
        request = self.request
        queryset = UserApplication.objects.filter(user_from=request.user)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user_to__username=self.kwargs['user_to_username'])
        return obj


class ApplicationDecision(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DecisionSerializer

    def post(self, request):
        serializer = DecisionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            data = serializer.validated_data
            set_decision(request, data["username"], data["decision"])
            return Response({"status": "decision is set"}, status=200)
        else:
            errors = serializer.errors
            return Response(errors, status=400)
