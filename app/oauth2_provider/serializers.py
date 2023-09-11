from rest_framework import serializers


class CustomAuthTokenSerializer(serializers.Serializer):
    client_id = serializers.CharField(label="Client ID", required=True)
    # client_secret = serializers.CharField(label="Client Secret", required=True)
    grant_type = serializers.ChoiceField(
        label="Grant Type",
        choices=["password", "refresh_token"],
        default="password",
    )
    username = serializers.CharField(label="Username", required=False)
    password = serializers.CharField(label="Password", required=False)
    refresh_token = serializers.CharField(label="Refresh Token", required=False)

    def validate(self, data):
        grant_type = data.get("grant_type")

        if grant_type == "refresh_token":
            # Nếu grant_type là "refresh_token", thiết lập username và password là không bắt buộc
            self.fields["username"].required = False
            self.fields["password"].required = False

            # Kiểm tra xem có cung cấp refresh_token hay không
            refresh_token = data.get("refresh_token")
            if not refresh_token:
                raise serializers.ValidationError(
                    "Refresh token is required for grant type 'refresh_token'"
                )

        else:
            # Nếu grant_type là "password", đảm bảo username và password là bắt buộc
            self.fields["username"].required = True
            self.fields["password"].required = True

        return data
