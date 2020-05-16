# -*- coding: utf-8 -*-
from django.urls import path

from authentication.views import login_view
from general.views import validate_password

urlpatterns = [
    path('validate_password', validate_password)
]