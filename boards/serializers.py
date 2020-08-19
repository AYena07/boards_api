from rest_framework import serializers
from boards.models import Board, Section, Sticker
from django.contrib.auth.models import User


class BoardSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    sections = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    invite_link = serializers.ReadOnlyField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'sections', 'users', 'invite_link']


class SectionSerializer(serializers.ModelSerializer):
    stickers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'title', 'board', 'stickers']


class UpdateSectionSerializer(serializers.ModelSerializer):
    stickers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    board = serializers.ReadOnlyField(source='board.id')

    class Meta:
        model = Section
        fields = ['id', 'title', 'board', 'stickers']


class StickerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sticker
        fields = ['id', 'title', 'text', 'section']


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
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.set_password(validated_data['password'])
        instance.save()

        return instance