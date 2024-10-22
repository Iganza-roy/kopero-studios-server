import uuid
from django.conf import settings
from django.db import models
from django.forms import ValidationError

from common.models import FlaggedModelMixin, TimeStampedModelMixin
from kopero_auth.models import Client, CrewMember
from services.models import Service
# from common.utils import generate_booking_number



class Booking(TimeStampedModelMixin, FlaggedModelMixin):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_bookings')
    service = models.ForeignKey(Client, on_delete=models.CASCADE)
    crew = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='photographer_bookings')
    is_booked = models.BooleanField(default=False)
    booking_number = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('served', 'Served'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def generate_booking_number(self):
        return str(uuid.uuid4())[:5]

    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = self.generate_booking_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.id} for {self.user.username}"
    
    def clean_time(self):
        # Ensure start_time is before end_time
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        if not self.is_available:
            raise ValidationError("The selected time slot is not available.")

class Review(TimeStampedModelMixin, FlaggedModelMixin):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_reviews')
    photographer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='photographer_reviews')
    rating = models.PositiveIntegerField()

    def __str__(self):
        return f"Review by {self.user.username} for photographer {self.photographer.full_name}"

    class Meta:
        unique_together = ('booking', 'user')

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")
