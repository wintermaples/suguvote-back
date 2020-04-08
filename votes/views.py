from rest_framework import viewsets

from votes.models import Vote
from votes.serializers import VoteRetrieveSerializer, VoteUpdateSerializer, VoteCreateSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VoteRetrieveSerializer
        elif self.action == 'create':
            return VoteCreateSerializer
        elif self.action == 'update':
            return VoteUpdateSerializer

        return VoteRetrieveSerializer
