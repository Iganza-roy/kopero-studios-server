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
    def get_image(self, obj):
        # Return the relative URL for the image
        return f"/media/{obj.image}" if obj.image else None
