from django.shortcuts import render
from rest_framework import viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        search_string = self.request.query_params.get('searchString', None)
        if search_string:
            queryset = User.objects.filter(username__icontains=search_string)
        else:
            queryset = User.objects.all()
        return queryset
