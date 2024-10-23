from django.db import models
from uuid import uuid4

# Create your models here.
class Service(models.Model):
    """
    Represents services database table
    """
    id = models.UUIDField(default=uuid4, primary_key=True)
    name = models.CharField(max_length=200, null=False, unique=True)
    tag = models.CharField(max_length=200, null=False)
    description = models.TextField(max_length=2000, blank=True)
    rate_per_hour = models.FloatField(default=1000.00)
    image = models.ImageField(upload_to="services", blank=True, null=True)

    def __str__(self):
        """Returns the official representation of a service"""
        return self.name
