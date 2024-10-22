from django.urls import path
from .views import AvailableTimeView, BookingListView, BookingDetailView

urlpatterns = [
    path("", BookingListView.as_view(), name="bookings"),
    path("<uuid:pk>/", BookingDetailView.as_view(), name="booking"),
    path('available-times/<uuid:crew_id>/', AvailableTimeView.as_view(), name='available_time'),
]