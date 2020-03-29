import json

from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework.response import Response

from users.models import User


@api_view(['POST'])
def login_view(request):
    user: User = authenticate(username=request.data['username'], password=request.data['password'])
    if user is not None:
        login(request, user)
        return Response(status=200)

    return Response(status=401)
