from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from django.core.mail import send_mail

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False
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


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные данные или пользователь не подтверждён.")
