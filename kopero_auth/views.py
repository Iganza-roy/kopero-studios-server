import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from common.views import BaseDetailView
from kopero_auth.models import Client, CrewMember
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    ClientSerializer,
    ClientUpdateSerializer,
    CrewMemberRegistrationSerializer,
    CrewMemberLoginSerializer,
    ClientLoginSerializer,
    ClientRegistrationSerializer,
    CrewSerializer,
    CrewUpdateSerializer,
    ReadClientSerializer,
    ReadCrewSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer
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

            return Response({
                "tokens": tokens,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "category": user.category,
                    "phone": user.phone
                    }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ClientLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ClientLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = serializer.get_tokens(user)

            return Response({
                "tokens": tokens,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "phone": user.phone
                    }
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


class ClientsListView(GenericAPIView):
    """
    API view to list Client users.

    This view supports filtering by role and pagination. If the 'all' 
    query parameter is provided, all clients matching the filters will 
    be returned without pagination.

    Attributes:
        model: The model class used for querying clients.
        serializer_class: The serializer class for serializing client data.
        read_serializer_class: The serializer class for read-only operations.

    Methods:
        get_read_serializer_class: Returns the appropriate serializer class for reading data.
        get_queryset: Retrieves a queryset of clients based on the request parameters.
        get: Handles GET requests to list clients.
    """

    model = Client
    serializer_class = ClientSerializer
    read_serializer_class = ReadClientSerializer

    def get_read_serializer_class(self):
        """
        Returns the serializer class to be used for reading data.
        
        If a read serializer class is defined, it will be used; otherwise,
        the default serializer class will be returned.
        """
        if self.read_serializer_class is not None:
            return self.read_serializer_class
        return self.serializer_class

    def get_queryset(self, request):
        """
        Retrieves a queryset of clients based on the 'role' filter.

        Args:
            request: The HTTP request object containing query parameters.

        Returns:
            QuerySet: A queryset of clients filtered by role and marked as not deleted.
        """
        queryset = []
        role = request.GET.get("role", None)  # Filter by role
        if role is not None:
            queryset = self.model.objects.filter(role=role, is_deleted=False)
        else:
            queryset = self.model.objects.filter(is_deleted=False) 
        return queryset

    def get(self, request):
        """
        Handles GET requests to list clients.

        If the 'all' query parameter is provided, all matching clients 
        will be returned. Otherwise, results will be paginated.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A response containing the serialized client data.
        """
        all_status = request.GET.get("all", None)
        queryset = self.get_queryset(request)
        if all_status is not None:
            serializer = self.get_read_serializer_class()(queryset, many=True)
            return Response(serializer.data) 
        else:  
            page = self.paginate_queryset(queryset)
            serializer = self.get_read_serializer_class()(page, many=True)
            return self.get_paginated_response(serializer.data)


class ClientDetailView(BaseDetailView):
    """
    API view to retrieve, update, or delete a Client user.

    This view handles operations for individual clients identified by 
    their primary key (PK).

    Attributes:
        permission_classes: The permission classes applied to this view.
        model: The model class used for querying clients.
        serializer_class: The serializer class for client operations.

    Methods:
        get_object: Retrieves a client object based on the primary key.
        get: Handles GET requests to retrieve a client’s details.
        put: Handles PUT requests to update a client’s information.
    """
    
    permission_classes = [IsAuthenticated]
    model = Client

    def get_object(self, pk):
        """
        Retrieves a Client object based on the provided primary key.

        Args:
            request: The HTTP request object.
            pk: The primary key of the client to retrieve.

        Returns:
            Client: The client object if found; raises 404 if not.
        """
        return get_object_or_404(Client, pk=pk)

    def get(self, request, pk=None):
        """
        Handles GET requests to retrieve a client’s details.

        Args:
            request: The HTTP request object.
            pk: The primary key of the client.

        Returns:
            Response: A response containing the serialized client data.
        """
        crew_member = self.get_object(pk)
        serializer = ClientSerializer(crew_member)
        return Response(serializer.data)

    def patch(self, request, pk=None):
        """
        Handles PATCH requests to update a crew member's details.
        Args:
            request: The HTTP request object containing updated data.
            pk: The primary key of the Crew Member.
        Returns:
            Response: A Response object indicating the result of the update operation.
        """
        client = self.get_object(pk)
        serializer = ClientUpdateSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Crew list and detail views
class CrewsListView(GenericAPIView):
    """
    View to handle listing Crew Members.

    This view allows for the retrieval of crew members, with optional filtering
    based on the 'category' field. It supports pagination and can return all 
    members if specified.

    Methods:
        get_read_serializer_class: Determines the appropriate serializer class 
                                    for read operations.
        get_queryset: Retrieves the queryset of crew members, applying any 
                      filters based on request parameters.
        get: Handles GET requests to return the list of crew members.
    """
    model = CrewMember
    serializer_class = CrewSerializer
    read_serializer_class = ReadCrewSerializer

    def get_read_serializer_class(self):
        """
        Returns the serializer class for read operations.

        If a custom read serializer is defined, it is returned; otherwise, the 
        default serializer is returned.
        """
        if self.read_serializer_class is not None:
            return self.read_serializer_class
        return self.serializer_class

    def get_queryset(self, request):
        """
        Retrieves the queryset of Crew Members based on request parameters.

        Filters the queryset based on the 'category' parameter in the request.
        Only non-deleted crew members are included in the results.

        Args:
            request: The HTTP request object.

        Returns:
            QuerySet: A queryset of CrewMember instances.
        """
        queryset = []
        category = request.GET.get("category", None)  # Retrieve the 'category' filter
        if category is not None:
            queryset = self.model.objects.filter(category=category, is_deleted=False)
        else:
            queryset = self.model.objects.filter(is_deleted=False)
        return queryset

    def get(self, request):
        """
        Handles GET requests to retrieve a list of crew members.

        If the 'all' parameter is provided, returns all crew members. Otherwise, 
        returns a paginated response.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A Response object containing the serialized data of crew members.
        """
        all_status = request.GET.get("all", None)
        queryset = self.get_queryset(request)
        if all_status is not None:
            serializer = self.get_read_serializer_class()(queryset, many=True)
            return Response(serializer.data) 
        else:  
            page = self.paginate_queryset(queryset)
            serializer = self.get_read_serializer_class()(page, many=True)
            return self.get_paginated_response(serializer.data)

class CrewDetailView(BaseDetailView):
    """
    View to handle operations on a specific Crew Member.

    This view allows for viewing, updating, or deleting a crew member based on 
    their unique identifier (primary key).

    Methods:
        get_object: Retrieves the specified crew member or the authenticated user.
        get: Handles GET requests to retrieve a crew member's details.
        put: Handles PUT requests to update a crew member's details.
    """
    permission_classes = [IsAuthenticated]
    model = CrewMember

    def get_object(self, pk):
        """
        Retrieves a Crew Member object by its primary key.

        If a primary key is provided, the corresponding object is fetched.
        Otherwise, the authenticated user object is returned.

        Args:
            request: The HTTP request object.
            pk: The primary key of the Crew Member.

        Returns:
            CrewMember: The corresponding Crew Member object or the authenticated user.
        """
        return get_object_or_404(CrewMember, pk=pk)

    def get(self, request, pk=None):
        """
        Handles GET requests to retrieve details of a crew member.

        Args:
            request: The HTTP request object.
            pk: The primary key of the Crew Member.

        Returns:
            Response: A Response object containing the serialized crew member data.
        """
        crew_member = self.get_object(pk)
        serializer = CrewSerializer(crew_member)
        return Response(serializer.data)

    def patch(self, request, pk=None):
        """
        Handles PATCH requests to update a crew member's details.
        Args:
            request: The HTTP request object containing updated data.
            pk: The primary key of the Crew Member.
        Returns:
            Response: A Response object indicating the result of the update operation.
        """
        crew_member = self.get_object(pk)
        serializer = CrewUpdateSerializer(crew_member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientPasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={"user_type": "client"})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CrewPasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={'user_type': 'crew'})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ClientPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'user_type': 'client'})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CrewPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data, context={'user_type': 'crew'})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
