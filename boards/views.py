from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.viewsets import GenericViewSet

from boards.models import Board, Section, Sticker
from boards.serializers import BoardSerializer, UserSerializer, SectionSerializer, StickerSerializer, UpdateSectionSerializer
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from boards.perm import IsOwnerOrBoardUser, IsSectionUser, IsStickerUser, IsAdminOrReadOnly
from django.db.models import Q
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating,
    deleting updating and watching
    detailed information
    """
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrBoardUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_anonymous:
            queryset = self.request.user.boards.all() | self.request.user.guest_boards.all()
        else:
            queryset = queryset.none()
        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['GET'])
    def sections(self, request, pk=None):
        board = self.get_object()
        return Response(SectionSerializer(board.sections.all(), many=True).data)

    @action(detail=True, methods=['GET'])
    def users(self, request, pk=None):
        board = self.get_object()
        return Response(UserSerializer(board.users.all(), many=True).data)

    @action(detail=True, methods=['GET'])
    def stickers(self, request, pk=None):
        board = self.get_object()
        return Response(StickerSerializer(Sticker.objects.all().filter(section__board=board), many=True).data)


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSectionUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_anonymous:
            queryset = queryset.filter(Q(board__users__id=user.id) | Q(board__owner__id=user.id))
        else:
            queryset = queryset.none()
        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        board_id = request.data['board']
        board = Board.objects.filter(pk=board_id)[0]
        if board.owner != request.user and request.user not in board.users.all():
            content = {
                'status': 'request was not permitted'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['GET'])
    def stickers(self, request, pk=None):
        section = self.get_object()
        return Response(StickerSerializer(section.stickers.all(), many=True).data)

    def get_serializer_class(self):
        if self.action == 'update':
            return UpdateSectionSerializer
        return super().get_serializer_class()


class StickerViewSet(viewsets.ModelViewSet):
    queryset = Sticker.objects.all()
    serializer_class = StickerSerializer
    permission_classes = [permissions.IsAuthenticated, IsStickerUser]

    def update(self, request, *args, **kwargs):
        print(request.data, args, kwargs)
        sticker = self.get_object()
        section = Section.objects.filter(pk=request.data['section'])[0]
        if str(sticker.section.board.id) != str(section.board.id):
            content = {
                'status': 'request was not permitted'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        if request.data['assigned_to'] not in sticker.section.board.users.all():
            content = {
                'status': 'request was not permitted'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_anonymous:
            queryset = queryset.filter(Q(section__board__users__id=user.id) | Q(section__board__owner__id=user.id))
        else:
            queryset = queryset.none()
        return queryset.distinct()

    def create(self, request, *args, **kwargs):
        section_id = request.data['section']
        section = Section.objects.filter(pk=section_id)[0]
        board = section.board
        if board.owner != request.user and request.user not in board.users.all():
            content = {
                'status': 'request was not permitted'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(id=request.data['assigned_to'])[0]
        if user not in board.users.all() and user != board.owner:
            content = {
                'status': 'request was not permitted'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)


class UserViewSet(GenericViewSet,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.UpdateModelMixin,):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    # permission class gives no permission for POST requests from default user,
    # however user creates instead
    def create(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)


@api_view(http_method_names=['POST'])
def invite(request, invite_id):
    pk = invite_id
    board = Board.objects.filter(invite_link=pk)
    if board:
        board = board[0]
        user = request.user
        if user.is_anonymous:
            content = {
                'status': 'you are not logged in'
            }
            return Response(content, status=status.HTTP_403_FORBIDDEN)
        else:
            if user not in board.users.all() and user != board.owner:
                board.invite_link = get_random_string()
                board.users.add(user)
                board.save()
            content = {
                'id': board.id
            }
            return Response(content)
    else:
        content = {
            'status': 'no such board'
        }
        return Response(content, status=status.HTTP_404_NOT_FOUND)


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
        })

