import jsonpickle
import jwt

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_bytes
from django.conf import settings
from django.urls import reverse
from django.http import JsonResponse

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .serializers import *
from .models import User
from .tasks import send_email_task


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        site = get_current_site(request).domain
        token = RefreshToken.for_user(user)
        url = reverse('email-verify')
        link = f"http://{site}{url}?token={token}"
        body = f"""
            Hi {user.name},
            Please use the link below to verify your password {link}
        """
        data = {
            "subject": "Verify your password",
            "body": body,
            "to": [user.email]
        }
        send_email_task.delay(data)
        return Response({"message": "We've sent you an email to verify your account"}, status=status.HTTP_201_CREATED)


class EmailVerificationView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    token = openapi.Parameter("token", openapi.IN_QUERY, description="token param", type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token])
    def get(self, request):
        try:
            token = request.GET.get('token')

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if user and not user.is_verified:
                user.is_verified = True
                user.save()
                return JsonResponse({"message": "Successfully activate"}, status=status.HTTP_200_OK)
        except jwt.exceptions.DecodeError as e:
            return JsonResponse({"error": "Token is invalid, please request a new one"}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.ExpiredSignatureError as e:
            return JsonResponse({"error": "Token's signature is expired, please request a new one"}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        email = request.data.get('email')

        user_qs = User.objects.filter(email=email)
        if user_qs.exists():
            user = user_qs[0]
            uidb64 = urlsafe_base64_encode(force_bytes(jsonpickle.encode(user)))
            token = PasswordResetTokenGenerator().make_token(user)
            site = get_current_site(request).domain
            url = reverse("reset-password-confirm", kwargs={
                "uidb64": uidb64,
                "token": token
            })
            link = f"http://{site}{url}"
            body = f"""
                Hi {user.name},
                Please use the link below to reset your password {link}
            """
            data = {
                "subject": "Reset your password",
                "body": body,
                "to": [user.email]
            }
            send_email_task.delay(data)
            return Response({"message": "We've sent you an email to reset your password"}, status=status.HTTP_200_OK)


class CheckPasswordResetTokenView(APIView):
    def post(self, request, uidb64, token):
        try:
            obj = smart_str(urlsafe_base64_decode(uidb64))
            user = jsonpickle.decode(obj)

            if not PasswordResetTokenGenerator().check_token(user,token):
                return Response({"error": "Token is invalid or signature is expired, please request a new one"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"success": True, "uidb64": uidb64, "token": token}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Token is invalid or signature is expired, please request a new one"}, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({"message": "Changed password successfully"}, status=status.HTTP_202_ACCEPTED)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)