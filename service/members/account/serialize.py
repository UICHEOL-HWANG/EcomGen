from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_pic', 'intro']
        read_only_fields = ['id']  # id는 읽기 전용으로 설정

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile_pic', 'intro']
        extra_kwargs = {'password': {'write_only': True}}  # 비밀번호는 쓰기 전용으로 설정

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile_pic=validated_data.get('profile_pic', None),
            intro=validated_data.get('intro', '')
        )
        return user
