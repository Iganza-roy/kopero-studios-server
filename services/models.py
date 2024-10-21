from django.db import models

# Create your models here.
class Service(models.Model):
    """
    Represents services database table
    """
    name = models.CharField(max_length=200, null=False)
    tag = models.CharField(max_length=200, null=False)
    description = models.TextField(max_length=2000, blank=True)
    rate_per_hour = models.FloatField(default=1000.00)
    image = models.ImageField(upload_to="services", blank=True, null=True)

    def __str__(self):
        """Returns the official representation of a service"""
        return self.name
