from django.conf import settings
from django.db import models
# from kopero_auth.models import User
# from services.models import Service


class AvailableTime(models.Model):
    # service = models.ForeignKey('Service', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # service = models.ForeignKey(Service, on_delete=models.CASCADE)
    # photographer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    session_time = models.ForeignKey(AvailableTime, on_delete=models.CASCADE)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.id} for {self.user.username}"
