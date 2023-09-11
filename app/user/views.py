import datetime
from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .permissions import OwnerUserPerms
from .serializers import (
    LoginSerializer,
    SignupSerializer,
    UserBaseInformationSerializer,
    UserInformationSerializer,
    UserListSerializer,
    ChangePasswordUserSerializer,
)
from .services import (
    gen_otp_and_token,
    check_valid_otp,
    send_email_password_forgot,
    check_password_forgot_core,
    send_email_password_change,
)
from .models import User
from rest_framework import status
from .response_handling import ErrorHandling, SuccessHandling
from .tasks import send_email_account_confirm_task, send_email_password_forgot_task

# django webform


@api_view(("POST",))
def verify_password_forgot(request, uidb64, token):
    """
    input: uidb64, token, password, password2
    - uidb64: ASCII decoding of user id
    - token: followed syntax username + email + exp 45 min + SECRET_KEY + algorithm = HS256
    workflow:
    - if password is the same as password2, and valid both uidb64 and token -> then change password
    - if not, response error
    """
    password = request.data.get("password", None)
    password2 = request.data.get("confirm_password", None)
    if password != password2:
        return Response({"error": "password is not the same"})
    if len(password) < 8:
        return Response({"error": "password at least 8 character"})
    else:
        check_password_forgot_core(uidb64, token, password)
    return Response("Reset account password successfully")


class UserViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ["change_password"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=["post"])
    def login(self, request):
        """
        when user login, they can login with username is email or phone
        Such as: username: tienle676@gmail.com , password: the_password_123
                 username: 0393258535          , password: the_password_123
        """
        email_or_phone = request.data.get("email_phone", None)
        password = request.data.get("password", None)

        user = authenticate(username=email_or_phone, password=password)

        if user:
            # check if user inactive
            if not user.is_active:
                username, email = user.username, user.email
                # return token_activation and code otp
                otp_code, token_activation = gen_otp_and_token(username, email)
                # send mail has code otp (task celery)
                send_email_account_confirm_task.delay(email, username, otp_code)
                # return token_activatation

                return Response(
                    ErrorHandling(
                        message="Tài khoản của bạn đã đăng ký nhưng chưa kích hoạt / Your account registered but you have not acivated yet",
                        code="FAILURE",
                        type="FAILURE",
                        lang="vi",
                        token_activation=token_activation,
                    ).to_representation(),
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            serializer = LoginSerializer(user)
            user.last_login = datetime.datetime.now()
            user.save()
            return Response(
                SuccessHandling(
                    message="Đăng nhập thành công / Login successfully",
                    code="SUCCESS",
                    type="SUCCESS",
                    lang="vi",
                    **serializer.data
                ).to_representation(),
                status=status.HTTP_200_OK,
            )

        return Response(
            ErrorHandling(
                message="Sai email hoặc mật khẩu / Your email or password is wrong",
                code="DATA INVALID",
                type="DATA INVALID",
                lang="vi",
            ).to_representation(),
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def signup(self, request):
        """
        input must include: username, email, phone, sex, password1, password2.
        then check valid -> if valid, then send email to authenticate
                         -> if not valid, then response error
        """
        data = request.data
        email = data.get("email", None)
        serializer = SignupSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            username, email = serializer.data["username"], serializer.data["email"]
            phone = serializer.data["phone"]
            if phone is not None and email is not None:
                # return token_activation and code otp
                otp_code, token_activation = gen_otp_and_token(username, email)
                # send mail has code otp
                send_email_account_confirm_task(
                    user_email=email, username=username, phone=phone, otp_code=otp_code
                )
                # return token_activatation
                return Response(
                    SuccessHandling(
                        message="Bạn đã đăng ký thành công / Your registration is successfully",
                        code="SUCCESS",
                        type="SUCCESS",
                        lang="vi",
                        token_activation=token_activation,
                    ).to_representation(),
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    ErrorHandling(
                        message="register by phone is not supported",
                        code="DATA INVALID",
                        type="DATA INVALID",
                        lang="vi",
                    ).to_representation(),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        error_message = [
            serializer.errors[error_name][0] for error_name in serializer.errors
        ][0]

        return Response(
            ErrorHandling(
                message=error_message,
                code="DATA INVALID",
                type="DATA INVALID",
                lang="vi",
            ).to_representation(),
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"])
    def verify(self, request):
        """
        input must include: otp_code, token_activation
        - otp_code is 6 number which is genenerated automatically
        - token_activation: is token followed syntax: username + email + otp_code + exp 5 min + SECRET_KEY + algorithm = HS256
        workflow:
        - if both otp_code and token_activation valid -> then activate account
        - if not, response error
        """
        data = request.data
        otp_code = data.get("otp_code", None)
        token_activation = data.get("token_activation", None)
        # check valid otp code
        is_valid, email = check_valid_otp(otp_code, token_activation)
        if is_valid == True:
            try:
                user = User.objects.get(email=email)
                user.is_active = True
                user.save()
                return Response(
                    SuccessHandling(
                        message="Xác thực của bạn đã thành công / Your verification is successfully",
                        code="SUCCESS",
                        type="SUCCESS",
                        lang="vi",
                    ).to_representation(),
                    status=status.HTTP_200_OK,
                )
            except:
                return Response(
                    ErrorHandling(
                        message="Địa chỉ email không tồn tại / The email has not existed",
                        code="DATA INVALID",
                        type="DATA INVALID",
                        lang="vi",
                    ).to_representation(),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                ErrorHandling(
                    message="500 Internal Server Error",
                    code="SERVER_DOWN",
                    type="SERVER_DOWN",
                    lang="vi",
                ).to_representation(),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def send_otp_code(self, request):
        data = request.data
        email = data.get("email", None)
        user = User.objects.get(email=email)
        if user:
            if user.is_active == False:
                otp_code, token_activation = gen_otp_and_token(
                    user.username, user.email
                )
                # send email has code otp
                send_email_account_confirm_task.delay(
                    user.email, user.username, otp_code
                )
                # return
                return Response(
                    SuccessHandling(
                        message="Bạn đã đăng ký thành công / Your registration is successfully",
                        code="SUCCESS",
                        type="SUCCESS",
                        lang="vi",
                        token_activation=token_activation,
                    ).to_representation(),
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    ErrorHandling(
                        message="You are already active",
                        code="DATA INVALID",
                        type="DATA INVALID",
                        lang="vi",
                    ).to_representation(),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            ErrorHandling(
                message="Email ERROR",
                code="DATA INVALID",
                type="DATA INVALID",
                lang="vi",
            ).to_representation(),
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"])
    def send_password_forgot(self, request):
        """
        input: email of forgot account
        workflow
        - if email exists, then send email to reset password
        - if not, response error
        """
        email = request.data.get("email", None)
        try:
            user = User.objects.get(email=email)
        except:
            return Response(
                ErrorHandling(
                    message="Địa chỉ email không tồn tại / The email has not existed",
                    code="DATA INVALID",
                    type="DATA INVALID",
                    lang="vi",
                ).to_representation(),
                status=status.HTTP_400_BAD_REQUEST,
            )

        send_email_password_forgot_task.delay(user_id=user.id)
        return Response(
            SuccessHandling(
                message="Email đặt lại mã pin đã gửi đến hộp thư của bạn",
                code="SUCCESS",
                type="SUCCESS",
                lang="vi",
            ).to_representation(),
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def password(self, request):
        """
        input:
            - password  : string
            - password2 : string
        workflow: check password same as password2 or not
        output: return error or sucess
        """
        data = request.data
        password = data.get("password", None)
        password2 = data.get("confirm_password", None)
        if password != password2:
            return Response(
                ErrorHandling(
                    message="Mật khẩu và mật khẩu xác nhận phải giống nhau / The password and confirmed password must match",
                    code="DATA INVALID",
                    type="DATA INVALID",
                    lang="vi",
                ).to_representation(),
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user
        user.set_password(password)
        user.save()
        send_email_password_change(user)
        return Response(
            SuccessHandling(
                message="Thay đổi mật khẩu thành công / Change your password successfully",
                code="SUCCESS",
                type="SUCCESS",
                lang="vi",
            ).to_representation(),
            status=status.HTTP_200_OK,
        )


class UserInformationViewSet(viewsets.ViewSet, generics.UpdateAPIView):
    queryset = User.objects.filter(is_active=True).select_related()
    serializer_class = UserInformationSerializer

    def get_permissions(self):
        if self.action in ["current_user"]:
            return [permissions.IsAuthenticated()]
        if self.action in ["update", "destroy", "partial_update", "change_password"]:
            return [OwnerUserPerms()]
        if self.action == "list":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return UserListSerializer
        if self.action in ["base_information"]:
            return UserBaseInformationSerializer
        return UserInformationSerializer

    @action(detail=False, methods=["get"])
    def base_information(self, request):
        """
        input:
            - header Authorization bearer token user
        workflow: check password same as password2 or not
        output: return error or sucess
        """
        return Response(
            self.serializer_class(request.user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @action(methods=["get"], url_path="current-user", detail=False)
    def current_user(self, request):
        """
        input:
            - header Authorization bearer token user
        workflow: check password same as password2 or not
        output: return error or sucess
        """
        return Response(
            self.serializer_class(request.user, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    @action(methods=["post"], url_path="change-password", detail=True)
    def change_password(self, request, pk):
        user = self.get_object()
        serializer = ChangePasswordUserSerializer(
            instance=user, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            SuccessHandling(
                message="đổi mật khẩu thành công / change password successful",
                code="SUCCESS",
                type="SUCCESS",
                lang="en",
            ).to_representation(),
            status=status.HTTP_200_OK,
        )


class UserGenderViewSet(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        data = [
            {"name": User.GENDER_FEMALE},
            {"name": User.GENDER_MALE},
            {"name": User.NONE},
        ]
        return Response(data=data, status=status.HTTP_200_OK)
