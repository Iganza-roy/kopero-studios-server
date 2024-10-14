from requests import Response
from .models import AvailableTime, Booking, Review
from rest_framework import serializers
from kopero_auth.models import User
from rest_framework import status

class AvailableTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableTime
        fields = '__all__'

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError("Start time must be before end time.")
        return attrs

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validate the data
        available_time = serializer.save()         # Save the instance
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        read_only_fields = ['is_booked']

    def validate(self, data):
        session_time = data['session_time']
        if session_time and session_time.is_booked:
            raise serializers.ValidationError("This time is already booked")
        if session_time.photographer != data['photographer']:
            raise serializers.ValidationError("Photographer is not available at this time")
        return data
    
    def create(self, validated_data):
        session_time = validated_data['session_time']
        session_time.is_booked = True
        session_time.is_available = False
        session_time.save()
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        if instance.is_booked:
            raise serializers.ValidationError("This booking is already confirmed")
        return super().update(instance, validated_data)
    
    def delete(self, instance):
        if instance.is_booked:
            raise serializers.ValidationError("This booking is already confirmed")
        return super().delete(instance)
    