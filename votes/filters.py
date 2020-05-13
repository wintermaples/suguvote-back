# -*- coding: utf-8 -*-
from django.db.models import Q
from django_filters import rest_framework as filters

from votes.models import Vote


class VoteFilter(filters.FilterSet):
    like = filters.CharFilter(method='like_filter', label='Like')
    ordering = filters.OrderingFilter(
        fields=('created_at', 'vote_count')
    )

    def like_filter(self, qs, name, value):
        return qs.filter(
            Q(title__icontains=value) | Q(description__icontains=value) | Q(tags__icontains=value)
        )

    class Meta:
        model = Vote
        fields = []
