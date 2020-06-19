# -*- coding: utf-8 -*-
from django.urls import path

from authentication.views import login_view, logout_view, is_logged_in_view

urlpatterns = [
    path('login/', login_view),
    path('logout/', logout_view),
    path('is_logged_in/', is_logged_in_view),
]