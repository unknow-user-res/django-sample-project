from pytz import NonExistentTimeError
from rest_framework import serializers
from . import google, facebook
from .services import register_social_google_user, register_social_facebook_user
from rest_framework.exceptions import AuthenticationFailed


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = google.Google.validate(auth_token)
        sub = user_data.get("sub")
        if not sub:
            raise serializers.ValidationError(
                {
                    "error": "Token đã hết hạn. Mời bạn đăng nhập lại. / "
                    "The token is invalid or expired. Please login again."
                }
            )

        # if user_data['aud'] != GOOGLE_CLIENT_ID:   # note HERE
        #     raise AuthenticationFailed('google client id not right')

        # user_id = user_data['sub']
        email = user_data.get("email")
        username = email.split("@")[0]
        picture = user_data.get("picture")
        print(username, email)
        # print(user_data) # {'iss': 'https://accounts.google.com', 'azp': '407408718192.apps.googleusercontent.com', 'aud': '407408718192.apps.googleusercontent.com', 'sub': '100341342189162789244', 'email': 'tienle676@gmail.com', 'email_verified': True, 'at_hash': 'KKgvDVtmpYA01qdFCfnSQA', 'name': 'Tiến Lê', 'picture': 'https://lh3.googleusercontent.com/a-/AOh14GhX0i1cNpso8Ufilymd2Jgfkn6I1Z7mjBvo_MEUWw=s96-c', 'given_name': 'Tiến', 'family_name': 'Lê', 'locale': 'vi', 'iat': 1628390059, 'exp': 1628393659}
        return register_social_google_user(email=email, username=username, avatar=picture)


class FacebookSocialAuthSerializer(serializers.Serializer):
    """Handles serialization of facebook related data"""

    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
        user_data = facebook.Facebook.validate(auth_token)
        try:
            fb_id = user_data.get("id")
            email = user_data.get("email", f"fb-id.{fb_id}@fb.id")
            username = email.split("@")[0]
            first_name = user_data.get("first_name")
            last_name = user_data.get("last_name")
            picture = user_data.get("picture").get("data").get("url")
            return register_social_facebook_user(
                fb_id=fb_id,
                email=email,
                name=username,
                first_name=first_name,
                last_name=last_name,
                avatar=picture,
            )

        except Exception as identifier:
            raise serializers.ValidationError(
                {
                    "error": "Token đã hết hạn. Mời bạn đăng nhập lại. / "
                    "The token is invalid or expired. Please login again."
                }
            )
