from django.urls import path
from .views import AvailableTimeDetailView, AvailableTimeListView, BookingListView, BookingDetailView

urlpatterns = [
    path("", BookingListView.as_view(), name="bookings"),
    path("<uuid:pk>/", BookingDetailView.as_view(), name="booking"),
    path('available-time/<uuid:photographer_id>/', AvailableTimeListView.as_view(), name='available_time_list_create'),

    # Endpoint to retrieve, update, or delete a specific available time slot
    path('available-time/<uuid:photographer_id>/<int:pk>/', AvailableTimeDetailView.as_view(), name='available_time_detail'),
]