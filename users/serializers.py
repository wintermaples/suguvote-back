# -*- coding: utf-8 -*-
from django.contrib.auth.password_validation import validate_password
from django.db.models import QuerySet
from rest_framework import serializers

from users.models import User


class UserRetrieveSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(UserRetrieveSerializer, self).__init__(*args, **kwargs)

        request = self.context['request']
        if request is None:
            raise AttributeError(f'${self.__class__.__name__} requires request in context!')

        request_user = request.user
        if isinstance(self.instance, QuerySet):
            target_user = self.instance.first()
        else:
            target_user = self.instance

        def get_allowed_fields():
            if target_user is None:
                return []

            if request_user is not None and request_user.id == target_user.id:
                return ['id', 'username', 'email', 'last_login', 'date_joined']
            else:
                return ['id', 'username']

        for field_key in self.fields.keys() - get_allowed_fields():
            self.fields.pop(field_key)

    class Meta:
        model = User
        fields = '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']
