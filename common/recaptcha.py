# -*- coding: utf-8 -*-
import json
import traceback

from django.conf import settings
import requests
from rest_framework.exceptions import APIException


def verify_recaptcha(token: str) -> bool:
    '''
    与えられたTokenから、ReCAPTCHAの成功/失敗を返します。
    何らかのエラーが発生した場合は、エラーを出力してFalseを返します。

    :param token: ReCAPTCHAのClient-Side側APIを叩いたときに取得したToken
    :return: ReCAPTCHAが成功している場合はTrue
    '''
    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': token
        })
        return bool(json.loads(response.text)['success'])
    except Exception as ex:
        traceback.print_exc(ex)
        return False


class ReCAPTCHAError(APIException):
    status_code = 400

    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)
