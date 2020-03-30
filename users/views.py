from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User
from users.serializers import UserRetrieveSerializer, UserCreateSerializer, UserUpdateSerializer


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):
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

    @action(detail=False)
    def me(self, request):
        if request.user is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(self.get_serializer(request.user).data)

    def perform_destroy(self, instance: User):
        instance.is_active = False
        instance.save()
