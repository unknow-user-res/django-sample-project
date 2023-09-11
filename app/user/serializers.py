from user.models import User
from rest_framework import serializers, exceptions
from datetime import date
import os
from django.core import exceptions as core_exceptions
from django.contrib.auth import password_validation, authenticate

def get_age(birthday):
    """
    get age based on year of birth
    value of age maybe return negative
    """
    today = date.today()
    age = (
        today.year
        - birthday.year
        - ((today.month, today.day) < (birthday.month, birthday.day))
    )
    return age


class LoginSerializer(serializers.ModelSerializer):
    """
    return access_token, refresh_token of user
    """

    class Meta:
        model = User
        fields = ("access_token", "refresh_token")
        read_only_fields = ["access_token", "refresh_token"]


class SignupSerializer(serializers.ModelSerializer):
    """
    create new user if data is validated,
    """

    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")
        error = password_validation.validate_password(password=password)

        # Method inherited from BaseForm
        if error:
            raise serializers.ValidationError({"error": error})
        if "confirm_password" in data.keys():
            if password != confirm_password:
                raise serializers.ValidationError(
                    {"error": "Mật khẩu và xác nhận mật khẩu phải giống nhau."}
                )
        elif confirm_password is None:
            raise serializers.ValidationError({"error": "Bạn chưa nhập lại mật khẩu."})
        return super().validate(data)

    def create(self, validated_data):
        """
        create new user
        """
        password = validated_data["password"]
        new_user = User(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        new_user.set_password(password)
        new_user.is_active = True
        new_user.save()

        return new_user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email"]


class UserInformationSerializer(serializers.ModelSerializer):
    # confirm_password = serializers.CharField(
    #     style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "birthday",
            "gender",
            "email",
            "avatar",
        ]
        extra_kwargs = {
            "username": {"read_only": True},
            "email": {"read_only": True},
        }

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "avatar":
                if instance.avatar:
                    try:
                        os.remove("media/" + instance.avatar.name)
                    except:
                        print("can't remove the picture")
                        pass
                instance.avatar = value
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class ChangePasswordUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "old_password", "password", "confirm_password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {"read_only": True},
            "email": {"read_only": True},
        }

    def validate(self, data):
        user = self.context["request"].user
        password = data["password"]
        confirm_password = data["confirm_password"]
        old_password = data["old_password"]
        user_ok = authenticate(username=user.email, password=old_password)
        if user_ok is None:
            raise serializers.ValidationError({"error": "Mật khẩu cũ không hợp lệ"})

        error = password_validation.validate_password(password=password)

        # Method inherited from BaseForm
        if error:
            raise serializers.ValidationError({"error": error})
        if "confirm_password" in data.keys():
            if password != confirm_password:
                raise serializers.ValidationError(
                    {"error": "Mật khẩu và xác nhận mật khẩu phải giống nhau."}
                )
        elif confirm_password is None:
            raise serializers.ValidationError({"error": "Bạn chưa nhập lại mật khẩu."})
        return super().validate(data)

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance


class UserBaseInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "avatar", "full_name"]
