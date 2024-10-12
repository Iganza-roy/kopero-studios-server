from .models import AvailableTime, Booking, Review
from rest_framework import serializers
from kopero_auth.models import User

class AvailableTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTime
        fields = '__all__'


class ReadBookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    photographer_name = serializers.CharField(source='photographer.full_name', read_only=True)
    session_time_slot = serializers.CharField(source='session_time.time_slot', read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'user', 'service', 'photographer', 'session_time', 'is_booked']
        read_only_fields = ['user', 'id', 'is_booked']


class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    photographer_name = serializers.CharField(source='photographer.full_name', read_only=True)
    session_time_slot = serializers.CharField(source='session_time.time_slot', read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'user', 'service', 'photographer', 'session_time', 'is_booked']
        read_only_fields = ['is_booked', 'service_name', 'photographer_name', 'session_time_slot']

    def validate(self, data):
        session_time = data.get('session_time')
        photographer = data.get('photographer')

        if session_time and session_time.is_booked:
            raise serializers.ValidationError("This time slot is already booked.")

        # Ensure the selected photographer matches the session time availability
        if session_time and photographer and session_time.photographer != photographer:
            raise serializers.ValidationError("The selected photographer is not available for this time slot.")
        
        return data
    
    def create(self, validated_data):
        session_time = validated_data['session_time']
        session_time.is_booked = True
        session_time.save()
        validated_data['status'] = 'pending'
        # Create the booking
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if instance.is_booked:
            raise serializers.ValidationError("This booking is already confirmed")
        return super().update(instance, validated_data)
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['booking', 'user', 'photographer', 'rating']

    def validate(self, data):
        # Ensure the service is completed before a review is allowed
        booking = data.get('booking')
        if booking.status != 'served':
            raise serializers.ValidationError("You can only review after the service is completed.")
        
        return data
