from django.shortcuts import render
from boards.models import Board
from boards.serializers import BoardSerializer
from django.http import Http404
from rest_framework import generics


class BoardList(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
# Create your views here.
