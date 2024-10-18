from datetime import date
from django.shortcuts import render
from requests import Response
from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Q
from booking.models import AvailableTime, Booking, Review
from booking.serializers import AvailableTimeSerializer, BookingSerializer, ReadBookingSerializer, ReviewSerializer
from common.views import ImageBaseListView, BaseDetailView, BaseListView
from kopero_auth.models import User

class BookingListView(BaseListView):
    permission_classes = [IsAuthenticated]
    model = Booking
    read_serializer_class = ReadBookingSerializer
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user  # Get the logged-in user
        
        # Filter bookings based on user role
        if user.is_photographer:
            queryset = queryset.filter(photographer=user)  # Show bookings where the user is the assigned photographer
        else:
            queryset = queryset.filter(user=user)  # Show bookings where the user is the one who made the booking
        
        # Further filtering based on query parameters (optional)
        q = self.request.GET.get("q", None)
        session_time = self.request.GET.get("session_time", None)
        service = self.request.GET.get("service_id", None)
        photographer = self.request.GET.get("photographer", None)

        kwargs = {}
        kwargs_ors = None

        if q is not None:
            kwargs_ors = Q(name__icontains=q)
        if service is not None:
            kwargs['service_id'] = service
        if session_time is not None:
            kwargs['session_time_id'] = session_time
        if photographer is not None and user.is_photographer:  # Restrict filtering by photographer for photographers only
            kwargs['photographer_id'] = photographer

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
        booking = self.get_object()

        # Ensure the booking is served and the user hasn't reviewed yet
        if booking.status != 'served':
            return Response({"detail": "You cannot review a booking until served."}, status=status.HTTP_400_BAD_REQUEST)
        
        review_exists = Review.objects.filter(booking=booking, user=request.user).exists()
        if review_exists:
            return Response({"detail": "You have already submitted a review for this booking."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the photographer cannot review themselves
        if request.user == booking.photographer:
            return Response({"detail": "Photographers cannot review themselves."}, status=status.HTTP_403_FORBIDDEN)
        
        # Create a new review
        review_data = {
            'booking': booking.id,
            'user': request.user.id,
            'photographer': booking.photographer.id,
            'rating': request.data.get('rating'),
        }
        review_serializer = ReviewSerializer(data=review_data)
        review_serializer.is_valid(raise_exception=True)
        review_serializer.save()

        return Response({"detail": "Review submitted successfully."}, status=status.HTTP_201_CREATED)


# class AvailableTimeView(APIView):
#     def get(self, request, photographer_id, date):
#         # Fetch available times for the specified photographer and date
#         available_times = AvailableTime.objects.filter(
#             photographer_id=photographer_id,
#             date=date,
#             is_available=True
#         ).values('start_time', 'end_time')

#         return Response(list(available_times), status=status.HTTP_200_OK)

class AvailableTimeListView(generics.ListCreateAPIView):
    queryset = AvailableTime.objects.all()
    serializer_class = AvailableTimeSerializer

    def perform_create(self, serializer):
        photographer_id = self.kwargs['photographer_id']
        serializer.save(photographer_id=photographer_id)


class AvailableTimeDetailView(generics.RetrieveAPIView):
    serializer_class = AvailableTimeSerializer

    def get_queryset(self):
        photographer_id = self.kwargs['photographer_id']
        date_str = self.request.query_params.get('date')

        if date_str:
            return AvailableTime.objects.filter(
                photographer_id=photographer_id,
                date=date_str,
                is_available=True
            )
        return AvailableTime.objects.none()


class PhotographerAvailabilityView(APIView):
    def get(self, request, photographer_id):
        # Get the session_time from request
        session_time_id = request.query_params.get('session_time')
        session_time = AvailableTime.objects.filter(id=session_time_id).first()

        if not session_time:
            return Response({"error": "Session time not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get the selected photographer's bookings during the selected session time
        selected_photographer_bookings = Booking.objects.filter(
            photographer_id=photographer_id,
            session_time=session_time
        )

        # Check if the selected photographer is busy
        if selected_photographer_bookings.exists():
            # Get the end time of the current booking (assuming each booking has a duration)
            next_available_time = selected_photographer_bookings.latest('session_time').session_time.end_time
        else:
            next_available_time = None

        # Now, find other available photographers during the same session time
        busy_photographers = Booking.objects.filter(
            session_time=session_time
        ).exclude(photographer_id=photographer_id).values_list('photographer_id', flat=True)

        available_photographers = User.objects.exclude(id__in=busy_photographers).filter(role='photographer')

        # Prepare the response data
        available_photographer_list = []
        for photographer in available_photographers:
            photographer_info = {
                "id": photographer.id,
                "full_name": photographer.full_name,
                "availability": f"Available during {session_time.time_slot}"
            }
            available_photographer_list.append(photographer_info)

        response_data = {
            "next_available_time": next_available_time.strftime("%Y-%m-%d %H:%M:%S") if next_available_time else "Available now",
            "available_photographers": available_photographer_list,
        }

        return Response(response_data, status=status.HTTP_200_OK)

class ReviewListView(BaseListView):
    model = Review
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        # Ensure the user can only see their own bookings to review
        user = self.request.user
        return Booking.objects.filter(user=user, status='served')

    def perform_create(self, serializer):
        booking_id = self.request.data.get('booking')
        booking = Booking.objects.get(id=booking_id)

        if booking.user != self.request.user:
            return Response({"detail": "You cannot review this booking."}, status=403)

        serializer.save(user=self.request.user, photographer=booking.photographer)
