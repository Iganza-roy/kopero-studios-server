from requests import Response
from .models import Booking, Review
from rest_framework import serializers
from rest_framework import status

class ReadBookingSerializer(serializers.ModelSerializer):
    """
    Handles serialization of data used to view Bookings
    """
    service_name = serializers.CharField(source='service.name', read_only=True)
    crew = serializers.CharField(source='crew.full_name', read_only=True)
    client = serializers.CharField(source='client.full_name', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'client', 'status', 'service_name', 'is_booked', 'crew', 'is_paid', 'date', 'time']
        read_only_fields = ['client', 'service', 'id', 'is_booked']


class BookingSerializer(serializers.ModelSerializer):
    """
    Handles serialization of data used to book a session
    """
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'client', 'service', 'booking_number', 'crew', 'total_price', 'is_booked', 'total_price', 'date', 'time']  # Include necessary fields
        read_only_fields = ['is_booked']

    def get_total_price(self, obj):
        # Assuming a fixed duration of 1 hour
        duration = 1  # in hours
        return duration * obj.service.rate_per_hour

    def validate(self, data):
        date = data.get('date')
        time = data.get('time')
        crew = data.get('crew')

        if Booking.objects.filter(crew=crew, date=date, time=time).exists():
            raise serializers.ValidationError("This time slot is already booked.")

        return data

    def create(self, validated_data):
        # Set status to 'pending'
        validated_data['status'] = 'pending'
        
        # Create the booking instance
        booking = Booking(**validated_data)
        booking.save()
        
        return booking

    def update(self, instance, validated_data):
        if instance.is_booked:
            raise serializers.ValidationError("This booking is already confirmed")
        return super().update(instance, validated_data)

    
class ReviewSerializer(serializers.ModelSerializer):
    """
    Handles serialization of data used to review a crew member
    """
    class Meta:
        model = Review
        fields = ['booking', 'user', 'crew_member', 'rating']

    def validate(self, data):
        # Ensure the service is completed before a review is allowed
        booking = data.get('booking')
        if booking.status != 'served':
            raise serializers.ValidationError("You can only review after the service is completed.")
        
        return data