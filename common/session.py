# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.crypto import get_random_string


def get_or_create_session_id(request) -> str:
    sess_id = request.session.get(settings.SESSION_ID_TAG, get_random_string())
    request.session[settings.SESSION_ID_TAG] = sess_id
    return sess_id
