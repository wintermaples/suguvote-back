import json

from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.models import User


@api_view(['POST'])
def login_view(request):
    if 'username' not in request.data or 'password' not in request.data:
        return Response(status=400)
    user: User = authenticate(username=request.data['username'], password=request.data['password'])
    if user is not None:
        login(request, user)
        return Response(status=200)

    return Response(status=401)


@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response(status=200)


@api_view(['GET'])
def is_logged_in_view(request):
    return Response(status=200, data={'is_logged_in': (not request.user.is_anonymous)})
