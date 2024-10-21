from rest_framework import serializers
from .models import BaseUser, Client, CrewMember
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = ["id", "email", "username", "first_name", "last_name"]


class CrewMemberRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CrewMember
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'category']

    def create(self, validated_data):
        user = CrewMember.objects.create_crew(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            category=validated_data['category']
        )

        return user

class ClientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Client
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        user = Client.objects.create_client(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        return user
    

class CrewMemberLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = CrewMember.objects.filter(email=email).first()
        if user:
            if check_password(password, user.password):
                return user
            else:
                raise serializers.ValidationError("Wrong password")
        else:
            raise serializers.ValidationError("Invalid login credentials")
    
    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
    

class ClientLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        user = Client.objects.filter(email=email).first()
        if user:
            if check_password(password, user.password):
                return user
            else:
                raise serializers.ValidationError("Wrong password")
        else:
            raise serializers.ValidationError("Invalid login credentials")
    
    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }
