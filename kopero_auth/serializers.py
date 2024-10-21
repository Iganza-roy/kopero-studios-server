from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Client, CrewMember
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password


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

class ReadClientSerializer(serializers.ModelSerializer):
    """
    Serializer class for a Client instance
    """

    class Meta:
        model = Client
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "is_active",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "full_name")


class ClientSerializer(serializers.ModelSerializer):
    """
    Serializer class for a Client instance for detail view
    """

    class Meta:
        model = Client
        fields = (
            "id",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "image",
            "bio",
            "is_active",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "full_name")


class ReadCrewSerializer(serializers.ModelSerializer):
    """
    Serializer class for a Client instance
    """

    class Meta:
        model = CrewMember
        fields = (
            "id",
            "email",
            "username",
            "category",
            "full_name",
            "phone",
            "image",
            "is_active",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "full_name")

class CrewSerializer(serializers.ModelSerializer):
    """
    Serializer class for a Crew instance for detail view
    """

    class Meta:
        model = CrewMember
        fields = (
            "id",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "image",
            "sessions_booked",
            "is_active",
            "category",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "full_name")