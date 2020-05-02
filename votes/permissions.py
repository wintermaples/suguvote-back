# -*- coding: utf-8 -*-
from rest_framework import permissions


class IsMatchedPasswordOrIsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        data = request.data
        return obj.creator == request.user or ('password' in data and obj.check_password(data['password']))
