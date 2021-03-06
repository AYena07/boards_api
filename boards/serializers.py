from rest_framework import serializers
from boards.models import Board, Section, Sticker, SetPasswordField
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


WRONG_EMAIL_OR_PASSWORD = 'Incorrect email address and / or password.'
USERNAME_IS_USED_BY_USER = 'Account with this username already exists.'


class BoardSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    owner_id = serializers.ReadOnlyField(source='owner.id')
    sections = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    invite_link = serializers.ReadOnlyField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'description', 'owner', 'owner_id', 'sections', 'users', 'invite_link']


class SectionSerializer(serializers.ModelSerializer):
    stickers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'title', 'description', 'board', 'stickers']


class UpdateSectionSerializer(serializers.ModelSerializer):
    stickers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    board = serializers.ReadOnlyField(source='board.id')

    class Meta:
        model = Section
        fields = ['id', 'title', 'description', 'board', 'stickers']


class StickerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sticker
        fields = ['id', 'title', 'text', 'section', 'assigned_to']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = SetPasswordField()

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

    @staticmethod
    def validate_username(username):
        if User.objects.filter(**{'{}__iexact'.format(User.USERNAME_FIELD): username}).exists():
            raise serializers.ValidationError(USERNAME_IS_USED_BY_USER)
        return username

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'boards', 'guest_boards', 'first_name', 'last_name')
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    boards = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    guest_boards = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    password = serializers.CharField(max_length=128, min_length=8,  required=True, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'boards', 'guest_boards', 'first_name', 'last_name')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.get('username'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.set_password(validated_data['password'])
        instance.save()

        return instance
