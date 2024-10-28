from django.urls import path
from .views import AvailableTimeView, BookingListView, BookingDetailView, cancel_booking, complete_booking, mark_as_paid

urlpatterns = [
    path("", BookingListView.as_view(), name="bookings"),
    path("<uuid:pk>/", BookingDetailView.as_view(), name="booking"),
    path('available-times/<uuid:crew_id>/', AvailableTimeView.as_view(), name='available_time'),
    path('<uuid:booking_id>/cancel/', cancel_booking, name='booking-cancel'),  # Cancel a booking
    path('<uuid:booking_id>/pay/', mark_as_paid, name='booking-pay'),  # Pay for a booking
    path('<uuid:booking_id>/complete/', complete_booking, name='booking-complete'),
]