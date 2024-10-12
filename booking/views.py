from django.shortcuts import render
from requests import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Q
from booking.models import Booking
from booking.serializers import BookingSerializer, ReadBookingSerializer
from common.views import ImageBaseListView, BaseDetailView, BaseListView

class BookingListView(BaseListView):
    model = Booking
    read_serializer_class = ReadBookingSerializer
    serializer_class = BookingSerializer
    
    #Filtering queryset based on query parameters
    def get_queryset(self):
        """
        Get the queryset for this view. 
        This must be an iterable, and may be a queryset (in which qs.query is available)
        """
        queryset = super().get_queryset()
        q = self.request.GET.get("q", None)
        user = self.request.GET.get("user", None)
        session_time = self.request.GET.get("session_time", None)
        service = self.request.GET.get("service_id", None)
        photographer = self.request.GET.get("photographer", None)

        kwargs = {}
        kwargs_ors = None

        if q is not None:
            kwargs_ors = Q(name__icontains=q)
        if service is not None:
            kwargs['service_id'] = service
        if user is not None:
            kwargs['user_id'] = user
        if photographer is not None:
            kwargs['photographer_id'] = photographer
        if session_time is not None:
            kwargs['session_time_id'] = session_time

        if kwargs_ors is not None:
            self.filter_object &= kwargs_ors  # Apply OR conditions
        if kwargs:
            self.filter_object &= Q(**kwargs)  # Apply AND conditions for specific fields

        if self.filter_object:
            queryset = queryset.filter(self.filter_object)

        return queryset

    def get(self, request):
        queryset = self.get_queryset()
        all_status = request.GET.get("all", None)

        if all_status is not None:
            serializer = self.get_read_serializer_class()(queryset, many=True, context={"request": request})
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(queryset)
            serializer = self.get_read_serializer_class()(page, many=True, context={"request": request})
    
    permission_classes = [IsAdminUser]
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
    

    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking, User, AvailableTime
from django.db.models import Q

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
