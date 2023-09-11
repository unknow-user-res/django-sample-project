import random
import jwt
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework import exceptions
from .models import User
from .response_handling import ErrorHandling, SuccessHandling

HOST, CLIENT = "HOST", "CLIENT_URL"


def gen_otp_and_token(username, email):
    """
    input: username and email of user
    generate otp_code randomly and use it to make token
    """
    random_code = "".join([str(random.randint(0, 9)) for i in range(6)])
    token = User.activate_token(username, email, random_code)

    return random_code, token


def check_valid_otp(otp_code, token):
    """
    decode the token, and get infor of decoded token to check valid
    workflow:
    - if valid return true and email
    - if not response error
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        if payload["type"] != "activate_token":
            raise exceptions.AuthenticationFailed(
                ErrorHandling(
                    message="Mã token của bạn không hợp lệ / Your token code is incorrect",
                    code="DATA INVALID",
                    type="DATA INVALID",
                    lang="vi",
                ).to_representation()
            )

        if payload["random_code"] != otp_code:
            raise exceptions.AuthenticationFailed(
                ErrorHandling(
                    message="Mã xác thực không hợp lệ / Your OTP code is incorrect",
                    code="DATA INVALID",
                    type="DATA INVALID",
                    lang="vi",
                ).to_representation()
            )

        email = payload["email"]
        return True, email

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


def send_email_password_change(user):
    """
    send mail to user when user change password
    """
    try:
        current_site = CLIENT
        mail_subject = "Change your password."
        email_recepient = user.email
        msg_html = render_to_string(
            "acc_password_change.html",
            {
                "useremail": user.email,
                "username": user.username,
            },
        )
        email = EmailMessage(mail_subject, msg_html, to=[email_recepient])
        email.content_subtype = "html"
        email.send(fail_silently=True)
    except:
        raise exceptions.server_error(
            ErrorHandling(
                message="Mã token đã hết hạn / Your token has expired",
                code="SERVER_DOWN",
                type="SERVER_DOWN",
                lang="vi",
            ).to_representation()
        )


def send_email_password_forgot(user):
    """
    send mail to user to reset password
    """
    try:
        current_site = CLIENT
        mail_subject = "Reset your password."
        email_recepient = user.email
        msg_html = render_to_string(
            "acc_password_forgot.html",
            {
                "username": user.username,
                "domain": current_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": User.reset_password_token(user),
            },
        )
        email = EmailMessage(mail_subject, msg_html, to=[email_recepient])
        email.content_subtype = "html"
        email.send(fail_silently=True)
    except:
        raise exceptions.server_error(
            ErrorHandling(
                message="Mã token đã hết hạn / Your token has expired",
                code="SERVER_DOWN",
                type="SERVER_DOWN",
                lang="vi",
            ).to_representation()
        )


def check_password_forgot_core(uidb64, token, password):
    """
    decode the token, and get infor of decoded token to check valid
    workflow:
    - if valid, then change password
    - if not response error
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        user_id_token = str(payload["id"])
        if payload["type"] != "reset_password_token":
            raise exceptions.AuthenticationFailed(
                ErrorHandling(
                    message="Mã token của bạn không hợp lệ / Your token code is incorrect",
                    code="DATA INVALID",
                    type="DATA INVALID",
                    lang="vi",
                ).to_representation()
            )
    except:
        raise exceptions.AuthenticationFailed(
            ErrorHandling(
                message="Mã token đã hết hạn / Your token has expired",
                code="DATA INVALID",
                type="DATA INVALID",
                lang="vi",
            ).to_representation()
        )
    try:
        user_id_uidb64 = force_str(urlsafe_base64_decode(uidb64))
    except:
        raise exceptions.AuthenticationFailed(
            ErrorHandling(
                message="Không thể giải mã uidb64 / Unable to decode uidb64",
                code="DATA INVALID",
                type="DATA INVALID",
                lang="vi",
            ).to_representation()
        )

    if user_id_uidb64 != user_id_token:
        raise exceptions.AuthenticationFailed(
            ErrorHandling(
                message="uidb64 không hợp lệ / uidb64 invalid",
                code="DATA INVALID",
                type="DATA INVALID",
                lang="vi",
            ).to_representation()
        )

    try:
        user = User.objects.get(id=user_id_token)
    except:
        raise exceptions.AuthenticationFailed(
            ErrorHandling(
                message="Email không tồn tại / Your email has not existed",
                code="DATA INVALID",
                type="DATA INVALID",
                lang="vi",
            ).to_representation()
        )

    user.set_password(password)
    if not user.is_active:
        user.is_active = True
        user.auth_google = True
    user.save()

    return user
