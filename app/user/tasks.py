from time import sleep
from celery import shared_task
import random
import jwt
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework import exceptions
from .models import User


@shared_task
def add_numbers():
    sleep(5)
    print("Running add numbers periodic task")


@shared_task
def add(x, y):
    return x + y


@shared_task()
def send_email_account_confirm_task(user_email, username, phone, otp_code):
    """
    input: email, username, otp_code
    send mail to email input
    """

    mail_subject = "Activate your account."
    email_recipient = user_email
    msg_html = render_to_string(
        "acc_active.html",
        {
            "phone": phone,
            "useremail": user_email,
            "username": username,
            "otp_code": otp_code,
        },
    )

    email = EmailMessage(mail_subject, msg_html, to=[email_recipient])
    email.content_subtype = "html"
    email.send(fail_silently=True)


@shared_task()
def send_email_password_forgot_task(user_id):
    """
    send mail to user to reset password
    """
    user = User.objects.get(id=user_id)
    current_site = "CLIENT_URL"
    mail_subject = "Reset your password."
    email_recipient = user.email
    link_reset_password = f"{current_site}/user/resetpassword/{urlsafe_base64_encode(force_bytes(user.pk))}/{User.reset_password_token(user)}"
    msg_html = render_to_string(
        "acc_password_forgot.html",
        {
            "username": user.username,
            "link_reset_password": link_reset_password,
            # 'domain': current_site,
            # 'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            # 'token': CustomUser.reset_password_token(user),
        },
    )
    email = EmailMessage(mail_subject, msg_html, to=[email_recipient])
    email.content_subtype = "html"
    email.send(fail_silently=True)
    return link_reset_password


# def
