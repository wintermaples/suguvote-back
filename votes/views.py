from datetime import datetime, timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from common.recaptcha import verify_recaptcha, ReCAPTCHAError
from common.session import get_or_create_session_id
from votes.filters import VoteFilter
from votes.models import Vote, VotingHistory
from votes.permissions import IsMatchedPasswordOrIsOwner
from votes.serializers import VoteRetrieveSerializer, VoteUpdateSerializer, VoteCreateSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.order_by('-created_at')
    filter_backends = [DjangoFilterBackend]
    filterset_class = VoteFilter

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

    def perform_create(self, serializer):
        data = self.request.data
        if 'recaptcha_token' not in data:
            raise ReCAPTCHAError('recaptcha_token is not set.')
        if not verify_recaptcha(data['recaptcha_token']):
            raise ReCAPTCHAError('ReCAPTCHA is failed.')
        return super().perform_create(serializer)

    @action(detail=True, methods=['GET', 'POST'])
    def voting_results(self, request, pk=None):
        vote: Vote = self.get_object()
        if request.method == 'GET':
            return Response(vote.get_voting_results())
        elif request.method == 'POST':
            data = request.data
            if 'answers' not in data:
                return Response(status=HTTP_400_BAD_REQUEST)

            if 'recaptcha_token' not in data:
                raise ReCAPTCHAError('recaptcha_token is not set.')
            if not verify_recaptcha(data['recaptcha_token']):
                raise ReCAPTCHAError('ReCAPTCHA is failed.')

            if vote.closing_at and vote.closing_at < datetime.now(timezone.utc):
                return Response(status=HTTP_400_BAD_REQUEST)

            if vote.is_voted_by(request):
                return Response(status=HTTP_400_BAD_REQUEST)

            vote.vote(request.data['answers'])
            vote.save()

            if request.user.is_anonymous:
                VotingHistory.objects.create(vote=vote, anonymous_user_session_id=get_or_create_session_id(request))
            else:
                VotingHistory.objects.create(vote=vote, user=request.user)

            return Response(self.get_object().get_voting_results())
