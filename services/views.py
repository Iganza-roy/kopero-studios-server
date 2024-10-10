from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import ServiceSerializer
from .models import Service

# Create your views here.
class ServiceViewSet(ModelViewSet):
    """
    Class based viewset for the service endpoint
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
