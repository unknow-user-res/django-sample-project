from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import (
    UserGenderViewSet,
    UserViewSet,
    UserInformationViewSet,
)

router = SimpleRouter()
router.register("users", UserViewSet, basename="users")
router.register(
    prefix="infor-user", viewset=UserInformationViewSet, basename="infor-user"
)
router.register(
    prefix="user-genders", viewset=UserGenderViewSet, basename="user-genders"
)
urlpatterns = [
    path("", include(router.urls)),
]
