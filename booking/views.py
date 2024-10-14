from django.shortcuts import render
from requests import Response
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Q
from booking.models import AvailableTime, Booking
from booking.serializers import AvailableTimeSerializer, BookingSerializer, ReadBookingSerializer
from common.views import ImageBaseListView, BaseDetailView, BaseListView
from kopero_auth.models import User
from rest_framework.permissions import IsAuthenticated

class BookingListView(BaseListView):
    permission_classes = [IsAuthenticated]
    model = Booking
    read_serializer_class = ReadBookingSerializer
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q", None)
        user_id = self.request.ET.get("user", None)
        session_time_id = self.request.GET.get("session_time", None)
        service_id = self.request.GET.get("service_id", None)
        photographer_id = self.request.GET.get("photographer", None)
        
        query_filter = Q()

        if q:
            query_filter &= Q(service__name__icontains=q)

        if session_time_id:
            query_filter &= Q(session_time_id=session_time_id)

        if service_id:
            query_filter &= Q(service_id=service_id)

        if photographer_id:
            query_filter &= Q(photographer_id=photographer_id)
        if user_id:
            query_filter &= Q(user_id=user_id)

        # Apply the combined filter conditions to the queryset
        return queryset.filter(query_filter)

    def get(self, request):
        all_status = request.GET.get("all", None)
        if all_status is not None:
            queryset = self.get_queryset()
            serializer = self.get_read_serializer_class()(
                queryset, many=True, context={"request": request}
            )
            return Response(serializer.data)
        else:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_read_serializer_class()(page, many=True, context={"request": request})
                return self.get_paginated_response(serializer.data)  # Return paginated response

            serializer = self.get_read_serializer_class()(queryset, many=True, context={"request": request})
            return Response(serializer.data)  # Fallback for when pagination is not used
    
    def delete(self, request, *args, **kwargs):
        booking = self.get_object()  # Get the specific booking instance
        if booking.is_booked:
            return Response({"detail": "This booking is already confirmed and cannot be deleted."}, status=status.HTTP_400_BAD_REQUEST)

        booking.delete()  # Delete the booking if allowed
        return Response({"detail": "Booking deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
class BookingDetailView(BaseDetailView):
    model = Booking
    read_serializer_class = ReadBookingSerializer
    serializer_class = BookingSerializer

    def get(self, request, pk):
        return super().get(request, pk)
    
    def delete(self, request, pk):
        return super().delete(request, pk)
    

class AvailableTimeView(APIView):
    def get(self, request, photographer_id, date):
        # Fetch available times for the specified photographer and date
        available_times = AvailableTime.objects.filter(
            photographer_id=photographer_id,
            date=date,
            is_available=True
        ).values('start_time', 'end_time')

        return Response(list(available_times), status=status.HTTP_200_OK)
    
class AvailableTimeListView(generics.ListCreateAPIView):
    queryset = AvailableTime.objects.all()
    serializer_class = AvailableTimeSerializer

# Retrieve, Update, and Destroy AvailableTime
class AvailableTimeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AvailableTime.objects.all()
    serializer_class = AvailableTimeSerializer