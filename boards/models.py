from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import re
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import CharField


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


STRONG_PASSWORD_VALIDATION_REGEX = r'^(?=.*[a-zA-Z])(?=.*\d).{8,}$'

WRONG_STRONG_PASSWORD_MESSAGE = 'Password must be at least 8 characters long, contain at least one digit'


def validate_password(password):
    if not bool(re.match(STRONG_PASSWORD_VALIDATION_REGEX, password)):
        raise ValidationError(WRONG_STRONG_PASSWORD_MESSAGE)
    return password


class SetPasswordField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs['write_only'] = True
        super().__init__(*args, **kwargs)

    def run_validators(self, value):
        validate_password(value)
        return super().run_validators(value)


class Board(models.Model):
    created = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200, default='', blank=True)
    owner = models.ForeignKey('auth.User', related_name='boards', on_delete=models.CASCADE)
    users = models.ManyToManyField(User, blank=True, related_name='guest_boards')
    invite_link = models.CharField(max_length=100, default=get_random_string)

    class Meta:
        ordering = ['created']


class Section(models.Model):
    created = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200, default='', blank=True)
    board = models.ForeignKey(Board, related_name="sections", on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']


class Sticker(models.Model):
    created = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=100)
    text = models.CharField(max_length=500)
    section = models.ForeignKey(Section, related_name="stickers", on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name="assigned_stickers",
                                    on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['created']
