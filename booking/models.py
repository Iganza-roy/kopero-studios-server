import uuid
from django.conf import settings
from django.db import models
from django.forms import ValidationError
from common.models import FlaggedModelMixin, TimeStampedModelMixin
from kopero_auth.models import Client, CrewMember
from services.models import Service

class Booking(TimeStampedModelMixin, FlaggedModelMixin):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_bookings')
    crew_member = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='crew_bookings')
    service = models.ForeignKey(Client, on_delete=models.CASCADE)
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

    def clean(self):
        # Ensure start_time is before end_time
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        
        # Ensure the selected time slot is available
        if Booking.objects.filter(
            crew_member=self.crew_member,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exists():
            raise ValidationError("The selected time slot is not available.")

    def __str__(self):
        return f"Booking {self.booking_number} for {self.client.username} with {self.crew_member.full_name}"

    class Meta:
        indexes = [
            models.Index(fields=['date', 'start_time', 'crew_member']),
        ]

class Review(TimeStampedModelMixin, FlaggedModelMixin):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_reviews')
    crew_member = models.ForeignKey(CrewMember, on_delete=models.CASCADE, related_name='crew_reviews')
    rating = models.PositiveIntegerField()

    def __str__(self):
        return f"Review by {self.client.username} for crew {self.crew_member.full_name}"

    class Meta:
        unique_together = ('booking', 'client')

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("Rating must be between 1 and 5.")
