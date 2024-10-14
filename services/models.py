from django.db import models

# Create your models here.
class Service(models.Model):
    """
    Represents services database table
    """
    name = models.CharField(max_length=200, null=True)
    tag = models.CharField(max_length=200, null=True)
    description = models.TextField(blank=True)
    rate_per_hour = models.FloatField(null=True)
    image = models.ImageField(upload_to="services", blank=True, null=True)

    def __str__(self):
        """Returns the official representation of a service"""
        return self.name
