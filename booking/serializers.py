from requests import Response
from .models import Booking, Review
from rest_framework import serializers
from rest_framework import status

class ReadBookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    crew_name = serializers.CharField(source='crew_member.full_name', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'client', 'status', 'service_name', 'is_booked']
        read_only_fields = ['client', 'service', 'crew_name', 'id', 'is_booked']


class BookingSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'client', 'service', 'crew_member', 'is_booked', 'total_price']
        read_only_fields = ['is_booked', 'service_name', 'total_price']

    def validate(self, data):
        session_time = data.get('session_time')  # Ensure this field exists
        crew_member = data.get('crew_member')

        if session_time and not session_time.is_available:
            raise serializers.ValidationError("This time slot is already booked.")

        # Ensure the selected crew member matches the session time availability
        if session_time and crew_member and session_time.crew_member != crew_member:
            raise serializers.ValidationError("The selected crew member is not available for this time slot.")
        
        return data
    
    def create(self, validated_data):
        session_time = validated_data['session_time']
        service = validated_data['service']

        # Calculate duration in hours for price calculation
        duration = (session_time.end_time.hour - session_time.start_time.hour) + \
                   (session_time.end_time.minute - session_time.start_time.minute) / 60
        
        total_price = duration * service.price_per_hour  # Assuming price_per_hour is defined in Service
        
        # Update session time availability
        session_time.is_available = False
        session_time.save()

        # Create the booking
        validated_data['total_price'] = total_price
        validated_data['status'] = 'pending'
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if instance.is_booked:
            raise serializers.ValidationError("This booking is already confirmed")
        return super().update(instance, validated_data)
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['booking', 'user', 'crew_member', 'rating']

    def validate(self, data):
        # Ensure the service is completed before a review is allowed
        booking = data.get('booking')
        if booking.status != 'served':
            raise serializers.ValidationError("You can only review after the service is completed.")
        
        return data