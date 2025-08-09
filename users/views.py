from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, ConfirmSerializer, LoginSerializer


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
