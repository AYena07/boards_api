from django.urls import path, include
from rest_framework.routers import DefaultRouter
from boards import views

router = DefaultRouter()
router.register(r'boards', views.BoardViewSet)
router.register(r'sections', views.SectionViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'stickers', views.StickerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
