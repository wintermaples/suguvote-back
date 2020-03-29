from django.shortcuts import render
from rest_framework import viewsets

from users.models import User
from users.serializers import UserRetrieveSerializer, UserCreateSerializer, UserUpdateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def get_serializer_class(self):
        return {
            'GET': UserRetrieveSerializer,
            'POST': UserCreateSerializer,
            'PUT': UserUpdateSerializer,
            'PATCH': UserUpdateSerializer,
        }[self.request.method]
