from datetime import date, timedelta
import datetime
from django.shortcuts import get_object_or_404, render
from requests import Response
from datetime import datetime
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Q
from booking.models import Booking, Review
from rest_framework.response import Response
from booking.serializers import BookingSerializer, ReadBookingSerializer, ReviewSerializer
from common.views import ImageBaseListView, BaseDetailView, BaseListView

class BookingListView(BaseListView):
    """
    Handles requests pertaining to all bookings
    """
    permission_classes = [IsAuthenticated]
    model = Booking
    read_serializer_class = ReadBookingSerializer
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user  # Get the logged-in user

        queryset = queryset.filter(Q(client=user) | Q(crew=user))
        
        q = self.request.GET.get("q", None)
        status_filter = self.request.GET.get("status", None)
        date_filter = self.request.GET.get("date", None)
        service = self.request.GET.get("service_id", None)

        kwargs = {}
        kwargs_ors = None

        if q is not None:
            kwargs_ors = Q(name__icontains=q)
        if service is not None:
            kwargs['service_id'] = service
        if status_filter is not None:
            kwargs['status'] = status_filter
        if date_filter is not None:
            kwargs['date'] = status_filter

        if kwargs_ors is not None:
            queryset = queryset.filter(kwargs_ors)
        if kwargs:
            queryset = queryset.filter(**kwargs)

        return queryset

    def get(self, request):
        queryset = self.get_queryset()
        all_status = request.GET.get("all", None)

        if all_status is not None:
            serializer = self.get_read_serializer_class()(queryset, many=True, context={"request": request})
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_read_serializer_class()(page, many=True, context={"request": request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_read_serializer_class()(queryset, many=True, context={"request": request})
            return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        booking = self.get_object()
        if booking.is_booked:
            return Response({"detail": "This booking is already confirmed and cannot be deleted."}, status=status.HTTP_400_BAD_REQUEST)

        booking.delete()
        return Response({"detail": "Booking deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class BookingDetailView(BaseDetailView):
    """
    Handles requests pertaining to specific booking
    """
    permission_classes = [IsAuthenticated]
    model = Booking
    read_serializer_class = ReadBookingSerializer
    serializer_class = BookingSerializer

    def get(self, request, pk):
        booking = self.get_object(request, pk) 
        
        # Check if the user is the client who made the booking
        if request.user != booking.client:
            return Response({"detail": "You do not have permission to view this booking."}, status=status.HTTP_403_FORBIDDEN)

        # If the booking is marked as served and the user hasn't reviewed yet, provide the option to review
        reviewed = Review.objects.filter(booking=booking, client=request.user).exists()
        
        if booking.status == 'served' and not reviewed:
            review_message = "Submit a review."
        else:
            review_message = None
        
        # Return booking details along with review option
        serializer = self.read_serializer_class(booking, context={"request": request})
        response_data = serializer.data
        if review_message:
            response_data['review_message'] = review_message
        
        return Response(response_data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        booking = self.get_object(request, pk)  # Pass request and pk here

        # Only allow deletion if the booking is not confirmed or served
        if booking.is_booked or booking.status == 'served':
            return Response({"detail": "This booking cannot be deleted as it is served."}, status=status.HTTP_400_BAD_REQUEST)

        booking.delete()
        return Response({"detail": "Booking deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, pk):
        """Handle submitting a review after the booking is served."""
        booking = self.get_object(request, pk)  # Pass request and pk here

        # Ensure the booking is served and the user hasn't reviewed yet
        if booking.status != 'served':
            return Response({"detail": "You cannot review a booking until served."}, status=status.HTTP_400_BAD_REQUEST)

        review_exists = Review.objects.filter(booking=booking, client=request.user).exists()
        if review_exists:
            return Response({"detail": "You have already submitted a review for this booking."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the photographer cannot review themselves
        if request.user == booking.crew:
            return Response({"detail": "Crew members cannot review their own bookings."}, status=status.HTTP_403_FORBIDDEN)

        # Create a new review
        review_data = {
            'booking': booking.id,
            'client': request.user.id,
            'crew': booking.crew.id,
            'rating': request.data.get('rating'),
        }
        review_serializer = ReviewSerializer(data=review_data)
        review_serializer.is_valid(raise_exception=True)
        review_serializer.save()

        return Response({"detail": "Review submitted successfully."}, status=status.HTTP_201_CREATED)
    

class ReviewListView(BaseListView):
    """
    View for reviews to different crew members
    """
    model = Review
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        user = self.request.user
        return Review.objects.filter(client=user)

    def perform_create(self, serializer):
        booking_id = self.request.data.get('booking')
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"detail": "Booking does not exist."}, status=404)

        if booking.client != self.request.user:
            return Response({"detail": "You cannot review this booking."}, status=403)

        serializer.save(client=self.request.user, crew=booking.crew)


class AvailableTimeView(APIView):
    """
    View for picking date and time to be used for booking
    """
    def get(self, request, crew_id):
        date = request.query_params.get('date')
        if not date:
            return Response({"error": "Date parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse the date string into a date object
        try:
            selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch booked times for the crew member on the specified date
        booked_times = Booking.objects.filter(
            crew_id=crew_id,
            date=selected_date
        ).values_list('time', flat=True)  # Get a flat list of booked times

        # Define working hours
        working_start = datetime.combine(selected_date, datetime.strptime('00:00:00', '%H:%M:%S').time())
        working_end = datetime.combine(selected_date, datetime.strptime('23:59:59', '%H:%M:%S').time())

        available_times = []
        current_time = working_start

        # Sort booked times
        booked_times = sorted(booked_times)

        # Check availability hour by hour
        while current_time < working_end:
            if current_time.time() not in booked_times:
                available_times.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': (current_time + timedelta(hours=1)).strftime('%H:%M')
                })
            current_time += timedelta(hours=1)

        return Response(available_times, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    print(f"Request User: {request.user}, Booking Client: {booking.client}")
    # Only the client can cancel the booking
    if booking.client.email != request.user.email:
        return Response({"detail": "You do not have permission to cancel this booking."}, status=403)

    # Update the booking status
    booking.update_status('canceled')
    return Response({"detail": "Booking canceled successfully."})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_paid(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.crew.email != request.user.email:
        return Response({"detail": "You do not have permission to mark this booking as paid."}, status=403)

    booking.mark_as_paid()
    return Response({"detail": "Booking marked as paid."})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Only the crew can complete the booking
    if booking.crew.email != request.user.email:
        return Response({"detail": "You do not have permission to complete this booking."}, status=403)

    booking.update_status('completed')
    return Response({"detail": "Booking marked as completed."})
