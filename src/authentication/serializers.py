import jsonpickle

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_bytes

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", 'name', "password")

    def validate(self, attrs):
        name = attrs.get('name')

        if not name.isalnum():
            raise AuthenticationFailed("Name should only contain alphanumeric characters")

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(read_only=True)
    tokens = serializers.JSONField(read_only=True)

    class Meta:
        model = User
        fields = ("email", 'password', "name", "tokens")

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials, please try again")
        if not user.is_active:
            raise AuthenticationFailed("Account is disabled, contact admin")
        if not user.is_verified:
            raise AuthenticationFailed("Account is not verified")

        return {
            "email": user.email,
            "name": user.name,
            "tokens": user.tokens()
        }


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SetNewPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(write_only=True)    
    token = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)    

    def validate(self, attrs):
        try:
            uidb64 = attrs.get('uidb64')
            token = attrs.get('token')
            password = attrs.get('password')

            obj = smart_str(urlsafe_base64_decode(uidb64))
            user = jsonpickle.decode(obj)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("Token is invalid or signature is expired, please request a new one")

            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise AuthenticationFailed("Token is invalid or signature is expired, please request a new one")


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs.get('refresh')
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except Exception as e:
            raise e