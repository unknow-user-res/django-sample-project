from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from .models import User


class CustomAuthenticationBackend(BaseBackend):
    """
    reference : https://docs.djangoproject.com/en/dev/topics/auth/customizing/#writing-an-authentication-backend
    """

    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(
                Q(email=username) | Q(username=username)
            )
            pwd_valid = user.check_password(password)
            if pwd_valid:
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
