from rest_framework.authentication import get_authorization_header, BaseAuthentication
from rest_framework import exceptions, status
from django.conf import settings
from .models import User
from .response_handling import ErrorHandling, SuccessHandling
import jwt

# class NotAuthenticated(exceptions.APIException):
#     status_code = status.HTTP_401_UNAUTHORIZED
#     default_detail = 'Authentication credentials were not provided.'


class JWTAuthentication(BaseAuthentication):
    """
    custom jwt for authentication
    """

    def authenticate(self, request):
        auth_header = get_authorization_header(request)
        auth_data = auth_header.decode("utf-8")

        auth_token = auth_data.split(" ")

        if not auth_token:
            return None

        if len(auth_token) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            return None

        elif len(auth_token) > 2:
            # Invalid token header. The Token string should not contain spaces. Do
            # not attempt to authenticate.
            return None

        token = auth_token[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user_id = payload["id"]
            print(payload)

            if payload["type"] != "access_token":
                raise exceptions.AuthenticationFailed(
                    ErrorHandling(
                        message="Mã token của bạn không hợp lệ / Your token code is incorrect",
                        code="DATA INVALID",
                        type="DATA INVALID",
                        lang="vi",
                    ).to_representation()
                )
            try:
                user = User.objects.get(id=user_id)
                # if not user.is_active:
                #     raise exceptions.AuthenticationFailed({'error': 'user inactive'})
            except:
                raise exceptions.NotFound({"error": "user is not exist"})

            return (user, token)

        except jwt.ExpiredSignatureError as ex:
            raise exceptions.AuthenticationFailed(
                ErrorHandling(
                    message="Mã token đã hết hạn / Your token has expired",
                    code="DATA INVALID",
                    type="DATA INVALID",
                    lang="vi",
                ).to_representation()
            )

        except jwt.DecodeError as ex:
            raise exceptions.AuthenticationFailed(
                ErrorHandling(
                    message="Mã token của bạn không hợp lệ / Your token code is incorrect",
                    code="DATA INVALID",
                    type="DATA INVALID",
                    lang="vi",
                ).to_representation()
            )

    def authenticate_header(self, request):
        return "provide"
