from django.db import models


class Board(models.Model):
    created = models.DateField(auto_now_add = True)
    title = models.CharField(max_length=100)

    class Meta:
        ordering = ['created']


