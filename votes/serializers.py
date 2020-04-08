# -*- coding: utf-8 -*-
import jsonschema
from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import UserRetrieveSerializer
from votes.models import Vote


class VoteRetrieveSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()

    def to_representation(self, instance):
        return {
            'pk': instance.pk,
            'creator': UserRetrieveSerializer(instance=instance.creator, context=self.context).data if instance.creator else None,
            'title': instance.title,
            'questions': instance.get_questions(),
            'created_at': instance.created_at,
            'updated_at': instance.updated_at
        }


class VoteCreateSerializer(serializers.Serializer):
    title = serializers.CharField(allow_null=False, allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=False)
    questions = serializers.JSONField(allow_null=False, required=True)

    def create(self, validated_data):
        if not self.context['request']:
            raise ValueError('You should set context["reqeust"]!')

        questions = validated_data.pop('questions')
        password = validated_data.pop('password', None)
        creator: AbstractBaseUser = self.context['request'].user

        if (password and creator.is_authenticated) or (not password and not  creator.is_authenticated):
            raise ValidationError('You should specify password when not logged in. Otherwise, you should "NOT" specify password!')

        if not Vote.validate_questions(questions):
            raise ValidationError('Wrong questions structure.')

        vote: Vote = Vote(**validated_data)
        vote.set_questions(questions)
        if password:
            vote.set_password(password)
        elif creator:
            vote.creator = creator
        vote.save()

        return vote

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def to_representation(self, instance):
        return VoteRetrieveSerializer(instance=instance, context=self.context).data


class VoteUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(allow_null=False, allow_blank=False, required=True)
    password = serializers.CharField(allow_blank=False, required=False)

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        if 'password' in validated_data and instance.creator:
            raise ValidationError('You cannot set password because creator is already set!')

        for k, v in validated_data.items():
            instance.__setattr__(k, v)

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()

        return instance

    def to_representation(self, instance):
        return VoteRetrieveSerializer(instance=instance, context=self.context).data
