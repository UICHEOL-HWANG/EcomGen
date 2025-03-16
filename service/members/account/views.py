from rest_framework import generics
from .serialize import UserSerializer, CreateUserSerializer
from .models import User
from rest_framework.permissions import AllowAny


# 회원 정보 모두 출력
class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserSerializer
        return UserSerializer


# 회원가입
class RegisterView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]
