from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def validate_password(request):
    if 'password' not in request.data:
        return Response(status=400)

    try:
        password_validation.validate_password(request.data['password'])
        return JsonResponse({
            'result': True
        })
    except ValidationError as error:
        return JsonResponse({
            'result': False,
            'error_messages': [str(error)[2:-2] for error in error.error_list]
        })
