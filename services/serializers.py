from rest_framework import serializers
from .models import Service


# Create serializers here
class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for the service model
    """
    class Meta:
        model = Service
        fields = "__all__"
