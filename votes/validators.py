# -*- coding: utf-8 -*-
from typing import List

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_tags(tags: any):
    if not tags:
        return

    try:
        if len(tags) > settings.MAX_TAG_COUNT:
            raise ValidationError('Tag count is over.')
        if any(map(lambda tag: len(tag) > settings.MAX_TAG_LENGTH, tags)):
            raise ValidationError('Tag length is over.')
        if any(map(lambda tag: tag == '', tags)):
            raise ValidationError('Some tag(s) is empty.')
        if len(tags) != len(set(tags)):
            raise ValidationError('Tags exist duplication.')
    except ValidationError as ve:
        raise ve
    except:
        raise ValidationError('Tag Validation Failed.')
