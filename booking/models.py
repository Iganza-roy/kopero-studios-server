from django.conf import settings
from django.db import models
# from kopero_auth.models import User
# from services.models import Service


class AvailableTime(models.Model):
    # service = models.ForeignKey('Service', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True)
    is_available = models.BooleanField(default=True)
    time_slot = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.photographer.full_name} - {self.service.name} on {self.date} from {self.start_time} to {self.end_time}"
    
    def save(self, *args, **kwargs):
        self.time_slot = f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ('service', 'photographer', 'date', 'start_time', 'end_time')

    def clean_time(self):
        # Ensure start_time is before end_time
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        if not self.is_available:
            raise ValidationError("The selected time slot is not available.")


class Booking(TimeStampedModelMixin, FlaggedModelMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_bookings')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    photographer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='photographer_bookings')
    session_time = models.ForeignKey(AvailableTime, on_delete=models.CASCADE)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking {self.id} for {self.user.username}"
