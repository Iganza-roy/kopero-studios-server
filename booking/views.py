from datetime import date, timedelta
import datetime
from django.shortcuts import render
from requests import Response
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Q
from booking.models import Booking, Review
from booking.serializers import BookingSerializer, ReadBookingSerializer, ReviewSerializer
from common.views import ImageBaseListView, BaseDetailView, BaseListView

class BookingListView(BaseListView):
    permission_classes = [IsAuthenticated]
    model = Booking
    read_serializer_class = ReadBookingSerializer
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user  # Get the logged-in user

        queryset = queryset.filter(Q(client=user) | Q(crew_member=user))
        
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
    permission_classes = [IsAuthenticated]
    model = Booking
    read_serializer_class = ReadBookingSerializer
    serializer_class = BookingSerializer

    def get(self, request, pk):
        booking = self.get_object()
        
        # Check if the user is the one who made the booking or if they are the photographer
        if request.user != booking.user and request.user != booking.photographer:
            return Response({"detail": "You do not have permission to view this booking."}, status=status.HTTP_403_FORBIDDEN)
        
        # If the booking is marked as served and the user hasn't reviewed yet, provide the option to review
        reviewed = Review.objects.filter(booking=booking, user=request.user).exists()
        
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
        booking = self.get_object()

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
        if request.user == booking.crew_member:
            return Response({"detail": "Crew members cannot review their own bookings."}, status=status.HTTP_403_FORBIDDEN)

        # Create a new review
        review_data = {
            'booking': booking.id,
            'client': request.user.id,
            'crew_member': booking.crew_member.id,
            'rating': request.data.get('rating'),
        }
        review_serializer = ReviewSerializer(data=review_data)
        review_serializer.is_valid(raise_exception=True)
        review_serializer.save()

        return Response({"detail": "Review submitted successfully."}, status=status.HTTP_201_CREATED)

class ReviewListView(BaseListView):
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

        serializer.save(client=self.request.user, crew_member=booking.crew_member)


class AvailableTimeView(APIView):
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
            crew_member_id=crew_id,
            date=selected_date
        ).values('start_time', 'end_time')

        # Create a list of booked time intervals
        booked_intervals = [(bt['start_time'], bt['end_time']) for bt in booked_times]

        # Add a time range to check for availability (e.g., 00:00 to 23:59)
        working_start = datetime.strptime('00:00:00', '%H:%M:%S').time()
        working_end = datetime.strptime('23:59:59', '%H:%M:%S').time()

        available_times = []
        current_time = working_start

        # Sort booked intervals by start time
        booked_intervals.sort()

        for start, end in booked_intervals:
            # Check for free time before the booked interval
            while current_time < start:
                next_time = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()
                if next_time <= start:  # Ensure the next time slot doesn't overlap
                    available_times.append({
                        'start_time': current_time.strftime('%H:%M'),
                        'end_time': next_time.strftime('%H:%M')
                    })
                current_time = next_time
            
            # Move the current time to the end of the booked interval
            current_time = end

        # Check for free time after the last booked interval
        while current_time < working_end:
            next_time = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()
            if next_time <= working_end:  # Ensure within working end
                available_times.append({
                    'start_time': current_time.strftime('%H:%M'),
                    'end_time': next_time.strftime('%H:%M')
                })
            current_time = next_time

        return Response(available_times, status=status.HTTP_200_OK)