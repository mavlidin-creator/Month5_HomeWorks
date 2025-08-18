from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken, RefreshToken as OAuthRefreshToken
from datetime import timedelta

from .serializers import RegisterSerializer, ConfirmSerializer, LoginSerializer, CustomTokenObtainPairSerializer
from .OAuth import get_google_user_info_by_code

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Регистрация успешна. Проверьте email и подтвердите кодом.'}, status=201)
        return Response(serializer.errors, status=400)


class ConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConfirmSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'message': 'Пользователь подтверждён. Теперь можно войти.'})
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=400)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        code = request.data.get("code")
        user_info = get_google_user_info_by_code(code)

        user, _ = User.objects.get_or_create(
            email=user_info["email"],
            defaults={
                "username": user_info["email"],
                "first_name": user_info.get("first_name", ""),
                "last_name": user_info.get("last_name", "")
            }
        )

        # OAuth2 токены через django-oauth-toolkit
        application = Application.objects.get(name="your_app")
        expires = timezone.now() + timedelta(seconds=3600)
        access_token = AccessToken.objects.create(
            user=user,
            application=application,
            token=AccessToken.generate_token(),
            expires=expires,
            scope="read write",
        )
        refresh_token = OAuthRefreshToken.objects.create(
            user=user,
            token=OAuthRefreshToken.generate_token(),
            application=application,
            access_token=access_token
        )

        return Response({
            "access_token": access_token.token,
            "refresh_token": refresh_token.token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })
