from django.shortcuts import render
from boards.models import Board
from boards.serializers import BoardSerializer, UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import renderers
from rest_framework import permissions
from boards.perm import IsOwnerOrReadOnly


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating,
    deleting updating and watching
    detailed information
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
