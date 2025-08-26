import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from datetime import timedelta
from oauth2_provider.models import Application, AccessToken, RefreshToken as OAuthRefreshToken
from django.core.mail import send_mail
from django.conf import settings

from .serializers import RegisterSerializer, ConfirmSerializer, LoginSerializer
from .redis_client import redis_instance
from .OAuth import get_google_user_info_by_code

User = get_user_model()


def send_welcome_email(user_email):
    subject = "Добро пожаловать!"
    message = "Спасибо за регистрацию. Мы рады видеть вас!"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Ошибка отправки письма: {e}")
        return False


def generate_code(length=6):
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            code = generate_code()
            redis_instance.setex(f"confirm:{user.email}", 300, code)

            # Отправляем email пользователю
            send_welcome_email(user.email)

            print(f"Confirmation code for {user.email}: {code}")  # Для теста
            return Response(
                {"message": "Регистрация успешна. Проверьте email и подтвердите код."},
                status=201
            )
        return Response(serializer.errors, status=400)


class ConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            code = serializer.validated_data.get("code")
            stored_code = redis_instance.get(f"confirm:{email}")
            if not stored_code:
                return Response({"error": "Код истёк или не найден"}, status=400)
            if stored_code != code:
                return Response({"error": "Неверный код"}, status=400)
            redis_instance.delete(f"confirm:{email}")
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            return Response({"message": "Пользователь подтверждён. Теперь можно войти."})
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "Неверные данные или пользователь не подтверждён"}, status=400)
            if not check_password(password, user.password):
                return Response({"error": "Неверные данные или пользователь не подтверждён"}, status=400)
            if not user.is_active:
                return Response({"error": "Пользователь не подтверждён"}, status=400)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response(serializer.errors, status=400)


class CustomTokenObtainPairView(TokenObtainPairView):
    pass  # можно использовать свой serializer если нужно


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
                "last_name": user.last_name
            }
        })
