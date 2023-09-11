import requests
from user.models import User
from django.conf import settings
from django.core.files.base import ContentFile
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauthlib.common import generate_token
from datetime import datetime, timedelta

DEFAULT_PASSWORD = settings.DEFAULT_PASSWORD


def register_social_google_user(email, username, avatar):
    user, created = User.objects.get_or_create(email=email)
    if created is True:
        user.username = username
        user.gender = user.GENDER_MALE
        user.set_password(DEFAULT_PASSWORD)
        user.save()

    if bool(user.avatar) is False:
        try:
            # Download picture and set avatar
            response = requests.get(avatar)
            avatar_data = response.content
            user.avatar.save("avatar.jpg", ContentFile(avatar_data))
        except:
            print("Can't get picture from account google")

    if not user.auth_google:
        user.is_active = True
        user.auth_google = True
        user.save()

    # get application
    app = Application.objects.get(name="Social Auth")
    # generate token
    token = generate_token()
    refresh_token = generate_token()

    # create access token
    expires = AccessToken.objects.create(
        user=user,
        application=app,
        token=token,
        expires=datetime.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS),
        scope="read write",
    )
    # create refresh token
    RefreshToken.objects.create(
        token=refresh_token, access_token=expires, application=app, user=user
    )
    return {
        "id": user.id,
        "access_token": token,
        "refresh_token": refresh_token,
        "scope": expires.scope,
        "expires": settings.TOKEN_EXPIRE_SECONDS,
    }


def register_social_facebook_user(fb_id, email, name, first_name, last_name, avatar):
    user, created = User.objects.get_or_create(fb_id=fb_id)
    if created is True:
        user.is_verified = True
        user.is_active = True
        user.auth_facebook = True
        user.username = name
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.gender = user.GENDER_MALE
        user.set_password(DEFAULT_PASSWORD)
        user.save()

    if bool(user.avatar) is False:
        try:
            # Download picture and set avatar
            response = requests.get(avatar)
            avatar_data = response.content
            user.avatar.save(f"fb_avatar_{fb_id}.jpg", ContentFile(avatar_data))
        except:
            print("Can't get picture from account facebook")

    if not user.auth_facebook:
        user.is_verified = True
        user.is_active = True
        user.auth_facebook = True
        user.save()
    # get application
    app = Application.objects.get(name="Social Auth")
    # generate token
    token = generate_token()
    refresh_token = generate_token()
    # create access token
    expires = AccessToken.objects.create(
        user=user,
        application=app,
        token=token,
        expires=datetime.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS),
        scope="read write",
    )
    # create refresh token
    RefreshToken.objects.create(
        token=refresh_token, access_token=expires, application=app, user=user
    )
    return {
        "id": user.id,
        "access_token": token,
        "refresh_token": refresh_token,
        "scope": expires.scope,
        "expires": settings.TOKEN_EXPIRE_SECONDS,
    }
