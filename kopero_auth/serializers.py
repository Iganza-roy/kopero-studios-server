from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Client, CrewMember
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext as _
import uuid


class CrewMemberRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializes data for handling crew member registration
    """
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
    """
    Serializes data for handling client registration
    """
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
    """
    Serializes data for logging in crew member
    """
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
    """
    Serializes data for logging in client
    """
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
    def get_image(self, obj):
        # Return the relative URL for the image
        return f"/media/{obj.image}" if obj.image else None


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
    def get_image(self, obj):
        # Return the relative URL for the image
        return f"/media/{obj.image}" if obj.image else None

class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['image', 'first_name', 'last_name', 'phone', 'bio']
    def get_image(self, obj):
        # Return the relative URL for the image
        return f"/media/{obj.image}" if obj.image else None


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
            "average_rating",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "full_name")
    def get_image(self, obj):
        # Return the relative URL for the image
        return f"/media/{obj.image}" if obj.image else None

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
            "average_rating",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("id", "full_name")
    def get_image(self, obj):
        # Return the relative URL for the image
        return f"/media/{obj.image}" if obj.image else None

class CrewUpdateSerializer(serializers.ModelSerializer):
    """
    Updating crew specific fields
    """
    class Meta:
        model = CrewMember
        fields = ['image', 'first_name', 'last_name', 'phone', 'bio',]
    def get_image(self, obj):
        # Return the relative URL for the image
        return f"/media/{obj.image}" if obj.image else None

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer class for sending password reset request
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        # For clients
        if self.context.get('user_type') == 'client':
            if not Client.objects.filter(email=value).exists():
                raise serializers.ValidationError(_("Client with this email does not exist"))
        # For crew members
        elif self.context.get('user_type') == 'crew':
            if not CrewMember.objects.filter(email=value).exists():
                raise serializers.ValidationError(_("Crew member with this email does not exist"))
        return value
    
    def save(self):
        email = self.validated_data['email']
        user_type = self.context.get('user_type')

        # Retrieve the appropriate user model
        user = Client.objects.get(email=email) if user_type == 'client' else CrewMember.objects.get(email=email)

        # Generate password reset token
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(user.pk.bytes)

        # Generate reset link
        reset_link = f'{settings.FRONTEND_URL}/reset-password-confirm/?uid={uid}&tk={token}'
        send_mail(
            subject="Password Reset Request",
            message=f"Click the following link to reset your password:\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email]
        )

class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer class for confirming password reset
    """
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = uuid.UUID(bytes=urlsafe_base64_decode(data["uidb64"]))
            user = Client.objects.get(pk=uid) if self.context.get('user_type') == 'client' else CrewMember.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Client.DoesNotExist, CrewMember.DoesNotExist):
            raise serializers.ValidationError(_("Invalid token or user ID"))

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError(_("Invalid or expired token"))
        
        return data

    def save(self):
        uid = uuid.UUID(bytes=urlsafe_base64_decode(self.validated_data['uidb64']))
        user = Client.objects.get(pk=uid) if self.context.get('user_type') == 'client' else CrewMember.objects.get(pk=uid)
        new_password = make_password(self.validated_data['new_password'])
        user.password = new_password
        user.save()
