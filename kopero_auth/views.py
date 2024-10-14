from django.shortcuts import render
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from dj_rest_auth.registration.views import VerifyEmailView, RegisterView
from dj_rest_auth.views import LoginView
# from dj_rest_auth.app_settings import create_token
from kopero_auth.serializers import (
    ReadUserSerializer, UserSerializer, RegisterNonAdminUserSerializer
)
from common.jwt import get_jwt
from datetime import timezone, datetime, timezone as dt_timezone
# from common.permissions import IsOpsAdmin
from kopero_auth.models import User
from django.utils import timezone
from common.views import BaseDetailView
from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from allauth.account.utils import send_email_confirmation
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from allauth.account.models import EmailAddress
import datetime
from django.utils import timezone
from uuid import UUID, uuid4 as uuid
from kopero_auth.models import Profile


class RegisterNonAdminUSerView(RegisterView):
    serializer_class = RegisterNonAdminUserSerializer


class UsersListView(GenericAPIView):
    """
    Users list view
    """
    permission_classes = [IsAuthenticated]
    model = User
    serializer_class = UserSerializer
    read_serializer_class = ReadUserSerializer

    def get_read_serializer_class(self):
        if self.read_serializer_class is not None:
            return self.read_serializer_class
        return self.serializer_class

    def get_queryset(self, request):
        # queryset = []
        role = request.GET.get("role", None)
        queryset = self.model.objects.filter(is_deleted=False)

        # Normalize the role to uppercase for consistent comparison
        if role:
            normalized_role = role.strip().upper()  # Normalize the input role
            queryset = queryset.filter(role=normalized_role)

        return queryset
    def get(self, request):
        all_status = request.GET.get("all", None)
        if all_status is not None:
            queryset = self.get_queryset(request)
            serializer = self.get_read_serializer_class()(queryset, many=True)
            return Response(serializer.data) 
        else:  
            queryset = self.get_queryset(request)
            page = self.paginate_queryset(queryset)
            serializer = self.get_read_serializer_class()(page, many=True)
            return self.get_paginated_response(serializer.data)


class UserDetailView(BaseDetailView):
    """
    Update, Delete, or View a User
    """
    model = User
    serializer_class = UserSerializer

    @permission_classes([IsAuthenticated])
    def get_object(self, request, pk):
        if pk is not None:
            return get_object_or_404(User, pk=pk)
        return request.user

    def get(self, request, pk=None):
        return super().get(request, pk)

    def put(self, request, pk=None):
        return super().put(request, pk)

    def delete(self, request, pk=None):
        item = self.get_object(request, pk)
        if hasattr(item, "is_deleted"):
            item.is_deleted = True
            item.deleted_at = datetime.datetime.now()
            item.modified_by = request.user
            new_email = str(item.id)+"@deleted.com"
            item.email = new_email
            email_address = EmailAddress.objects.get(user__exact=item.id)
            email_address.email = new_email
            item.is_active = False
            email_address.save()
            item.save()
        else:
            item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PhotographersListView(GenericAPIView):
    """
    List view for users with the photographer role
    """
    permission_classes = [IsAuthenticated]
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.model.objects.filter(role__icontains='photographer', is_deleted=False)

    def get(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)


class PhotographerDetailView(GenericAPIView):
    """
    Detail view for a specific photographer
    """
    permission_classes = [IsAuthenticated]
    model = User
    serializer_class = UserSerializer

    def get_object(self, pk):
        # No need to cast pk to UUID manually, let Django handle it
        return get_object_or_404(User, pk=pk, role__iexact='photographer', is_deleted=False)

    def get(self, request, pk=None):
        photographer = self.get_object(pk)
        serializer = self.serializer_class(photographer)
        return Response(serializer.data)

    def put(self, request, pk=None):
        photographer = self.get_object(pk)
        serializer = self.serializer_class(photographer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        photographer = self.get_object(pk)
        photographer.is_deleted = True
        photographer.deleted_at = datetime.datetime.now()
        photographer.modified_by = request.user
        photographer.email = f"{photographer.id}@deleted.com"

        # Handle EmailAddress if exists
        try:
            email_address = EmailAddress.objects.get(user=photographer)
            email_address.email = photographer.email
            email_address.save()
        except EmailAddress.DoesNotExist:
            pass

        photographer.is_active = False
        photographer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def create_auth_token(request):
    token, created = Token.objects.get_or_create(user=request.user)
    return Response(token.key, status=status.HTTP_201_CREATED)

# @receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    user = email_address.user
    if user.profile is None:
            profile = Profile.objects.create(user=user)
    else:
            profile = user.profile
    profile.email_confirmed = True
    profile.save()


