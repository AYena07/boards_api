from django.shortcuts import render
from boards.models import Board,Section
from boards.serializers import BoardSerializer, UserSerializer, SectionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from boards.perm import IsOwner
from rest_framework.generics import get_object_or_404


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating,
    deleting updating and watching
    detailed information
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated,
                          IsOwner]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Board.objects.all()
        try:
            username = self.request.user
            if username is not None:
                queryset = queryset.filter(owner=username)
        except TypeError:
            return Board.objects.none()
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Section.objects.all()
        try:
            username = self.request.user
            if username is not None:
                queryset = queryset.filter(board__owner=username)
        except TypeError:
            return Section.objects.none()
        return queryset

    def create(self, request, *args, **kwargs):
        # print(request.user)
        board_id = request.data['board']
        board = Board.objects.filter(pk=board_id)
        if board[0].owner != request.user:
            content = {
                'status': 'request was not permitted'
            }
            return Response(content)
        return super().create(request, *args, **kwargs)


class UserViewSet(viewsets.ReadOnlyModelViewSet,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

