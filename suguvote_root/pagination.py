# -*- coding: utf-8 -*-
from rest_framework.pagination import PageNumberPagination


class SuguvoteDefaultPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = 'size'
