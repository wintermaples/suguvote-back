# -*- coding: utf-8 -*-
from rest_framework.throttling import UserRateThrottle


class VotingThrottle(UserRateThrottle):
    scope = 'voting'

    def allow_request(self, request, view):
        if request.method == 'GET':
            return True
        return super().allow_request(request, view)


class CreateVoteThrottle(UserRateThrottle):
    scope = 'create_vote'
