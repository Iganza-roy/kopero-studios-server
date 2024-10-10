from django.shortcuts import render
from requests import Response
from django.db.models import Q
from booking.models import Booking
from booking.serializers import BookingSerializer, ReadBookingSerializer
from common.views import ImageBaseListView, BaseDetailView

class BookingListView(ImageBaseListView):
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
            serializer = self.get_read_serializer_class()(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        
class BookingDetailView(BaseDetailView):
    model = Booking
    read_serializer_class = ReadBookingSerializer
    serializer_class = BookingSerializer

    def get(self, request, pk):
        return super().get(request, pk)
    
    def delete(self, request, pk):
        return super().delete(request, pk)
    

    