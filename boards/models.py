from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Board(models.Model):
    created = models.DateField(auto_now_add = True)
    title = models.CharField(max_length=100)
    owner = models.ForeignKey('auth.User', related_name='boards', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']
