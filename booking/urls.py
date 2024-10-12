from django.urls import path
from .views import BookingListView, BookingDetailView, PhotographerAvailabilityView

urlpatterns = [
    path("", BookingListView.as_view(), name="bookings"),
    path("<uuid:pk>/", BookingDetailView.as_view(), name="booking"),
    path("photographers/<int:photographer_id>/availability/", 
         PhotographerAvailabilityView.as_view(), name='photographer-availability'),
]