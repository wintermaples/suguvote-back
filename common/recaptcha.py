# -*- coding: utf-8 -*-
from django.conf import settings
import requests


def verify_recaptcha(token: str) -> bool:
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': token
    })
    return bool(response.content)
