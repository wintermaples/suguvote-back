from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from votes import voter
from votes.models import Vote
from votes.serializers import VoteRetrieveSerializer, VoteUpdateSerializer, VoteCreateSerializer


# TODO: Implement permission of deleting.
class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}

    def get_serializer_class(self):
        return {
            'list': VoteRetrieveSerializer,
            'create': VoteCreateSerializer,
            'retrieve': VoteRetrieveSerializer,
            'update': VoteUpdateSerializer,
            'partial_update': VoteUpdateSerializer,
        }[self.action]

    @action(detail=True, methods=['GET', 'POST'])
    def voting_results(self, request, pk=None):
        if request.method == 'GET':
            return Response(self.get_object().get_voting_results())
        elif request.method == 'POST':
            self.get_object().vote(request.data['answers'])
            return Response(self.get_object().get_voting_results())
