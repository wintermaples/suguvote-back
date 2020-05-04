from datetime import datetime, timezone

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from common.recaptcha import verify_recaptcha
from votes import voter
from votes.models import Vote
from votes.permissions import IsMatchedPasswordOrIsOwner
from votes.serializers import VoteRetrieveSerializer, VoteUpdateSerializer, VoteCreateSerializer


# TODO: Implement permission of deleting.
class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.order_by('-created_at')
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'vote_count']

    def get_serializer_context(self):
        return {'request': self.request}

    def get_serializer_class(self):
        serializers = {
            'list': VoteRetrieveSerializer,
            'create': VoteCreateSerializer,
            'retrieve': VoteRetrieveSerializer,
            'update': VoteUpdateSerializer,
            'partial_update': VoteUpdateSerializer,
        }
        return serializers[self.action] if self.action in serializers else VoteRetrieveSerializer

    def get_permissions(self):
        permission_classes = []
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsMatchedPasswordOrIsOwner]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['GET', 'POST'])
    def voting_results(self, request, pk=None):
        vote: Vote = self.get_object()
        if request.method == 'GET':
            return Response(vote.get_voting_results())
        elif request.method == 'POST':
            data = request.data
            if 'answers' not in data or 'recaptcha_token' not in data:
                return Response(status=HTTP_400_BAD_REQUEST)

            if not verify_recaptcha(data['recaptcha_token']):
                return Response('ReCAPTCHA is failed.', status=HTTP_400_BAD_REQUEST)

            if vote.closing_at and vote.closing_at < datetime.now(timezone.utc):
                return Response(status=HTTP_400_BAD_REQUEST)

            vote.vote(request.data['answers'])
            vote.save()
            return Response(self.get_object().get_voting_results())
