from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from boards import views

urlpatterns = [
    path('boards/', views.BoardList.as_view()),
    path('boards/<int:pk>', views.BoardDetail.as_view()),
]

