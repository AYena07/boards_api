from django.urls import path, include
from rest_framework.routers import DefaultRouter
from boards import views

router = DefaultRouter();
router.register(r'boards', views.BoardViewSet)

urlpatterns = [
    path('', include(router.urls))
]

