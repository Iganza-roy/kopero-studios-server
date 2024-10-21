from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    CrewMemberRegistrationSerializer,
    CrewMemberLoginSerializer,
    ClientLoginSerializer,
    ClientRegistrationSerializer,
    UserSerializer
)


class CrewMemberRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CrewMemberRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "message": "Crew member registered successfully",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClientRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response({
                "message": "Client registered successfully",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CrewMemberLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CrewMemberLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = serializer.get_tokens(user)
            # user_serializer = UserSerializer(user)

            return Response({
                "tokens": tokens
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ClientLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClientLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = serializer.get_tokens(user)
            # user_serializer = UserSerializer(user)

            return Response({
                "tokens": tokens
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
