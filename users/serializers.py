from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.generate_confirmation_code()

        send_mail(
            subject='Подтверждение регистрации',
            message=f'Ваш код подтверждения: {user.confirmation_code}',
            from_email='noreply@example.com',
            recipient_list=[user.email],
        )

        return user


class ConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data['email'], confirmation_code=data['code'])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Неверный email или код.")
        user.is_active = True
        user.confirmation_code = ''
        user.save()
        return data


User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверные данные или пользователь не подтверждён.")
        
        if not check_password(data['password'], user.password):
            raise serializers.ValidationError("Неверные данные или пользователь не подтверждён.")

        if not user.is_active:
            raise serializers.ValidationError("Пользователь не подтверждён.")

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["birthday"] = str(user.birthday) if user.birthday else None
        return token
