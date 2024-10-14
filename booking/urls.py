from django.urls import path
from .views import AvailableTimeDetailView, AvailableTimeListView, BookingListView, BookingDetailView

urlpatterns = [
    path("", BookingListView.as_view(), name="bookings"),
    path("<uuid:pk>/", BookingDetailView.as_view(), name="booking"),
    path('available-time/', AvailableTimeListView.as_view(), name='available-time-list-create'),
    path('available-time/<uuid:pk>/', AvailableTimeDetailView.as_view(), name='available-time-detail'),
]