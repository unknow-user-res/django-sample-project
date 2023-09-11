from datetime import datetime, timedelta
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q
from django.core.validators import RegexValidator
import jwt
from PIL import Image
from django.contrib.postgres.fields import ArrayField


class User(AbstractUser):
    NONE = "None"
    # Sex
    GENDER_MALE = "Male"
    GENDER_FEMALE = "Female"
    GENDERS = (
        (GENDER_MALE, _("Male")),
        (GENDER_FEMALE, _("Female")),
        (NONE, _("None")),
    )

    # Role
    ROLE = ((NONE, "None"),)

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(_("Email address"), max_length=50, unique=True)

    # auth by google or facebook
    auth_google = models.BooleanField(_("Auth Google"), default=False)
    auth_facebook = models.BooleanField(_("Auth Facebook"), default=False)
    facebook_id = models.CharField(
        _("Facebook id"), max_length=50, blank=True, null=True
    )

    birthday = models.DateField(_("Birthday"), null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=6, choices=GENDERS, default=NONE)
    # role user for dev
    avatar = models.ImageField(
        _("Avatar"), null=True, upload_to="users/%Y/%m", blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def set_gender_male(self):
        self.gender = self.GENDER_MALE
        self.save()

    def set_gender_female(self):
        self.gender = self.GENDER_FEMALE
        self.save()

    def set_gender_none(self):
        self.gender = self.NONE
        self.save()

    @property
    def full_name(self):
        "Returns the person's full name."
        if self.first_name:
            return "%s %s" % (self.last_name, self.first_name)
        if self.username:
            return self.username
        if self.email:
            return self.email.split("@")[0]
        return self.phone

    @property
    def age(self):
        if self.birthday:
            return datetime.now().year - self.birthday.year
        return 0

    @property
    def access_token(self):
        """
        access token for user login
        """
        token = jwt.encode(
            {
                "id": self.id,
                "type": "access_token",
                "username": self.username,
                "email": self.email,
                "exp": datetime.utcnow() + timedelta(days=1),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return token

    @property
    def refresh_token(self):
        """
        refresh token for user login
        """
        token = jwt.encode(
            {
                "id": self.id,
                "type": "refresh_token",
                "username": self.username,
                "email": self.email,
                "exp": datetime.utcnow() + timedelta(days=27),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return token

    @staticmethod
    def activate_token(username, email, random_code):
        """
        activate token for activating account
        """
        token = jwt.encode(
            {
                "type": "activate_token",
                "username": username,
                "email": email,
                "random_code": random_code,
                "exp": datetime.utcnow() + timedelta(minutes=5),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return token

    @staticmethod
    def reset_password_token(user):
        """
        reset_password_token for reset password when user forgot password
        """
        token = jwt.encode(
            {
                "id": user.id,
                "type": "reset_password_token",
                "username": user.username,
                "email": user.email,
                "exp": datetime.utcnow() + timedelta(minutes=45),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return token
