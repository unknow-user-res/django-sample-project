from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.conf import settings
import views

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register(
    prefix="send-email-template-test",
    viewset=views.SendEmailTemplateTest,
    basename="send-email-template-test",
)


urlpatterns = [
    path("", include(router.urls)),
]
