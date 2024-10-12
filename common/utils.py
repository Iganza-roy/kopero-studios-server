import random
import string
from django.db.models import Max
from booking.models import Booking

def generate_booking_number():
    """Generates a unique booking number in the format AADADD0001 with incrementing numbers."""

    random_letters = ''.join(random.choices(string.ascii_uppercase, k=6))
    last_booking_number = Booking.objects.aggregate(Max('booking_number'))['booking_number__max']
    
    if last_booking_number:
        last_number = int(last_booking_number[-4:])
        new_number = f"{last_number + 1:04d}"
    else:
        new_number = "0001"
    return f"{random_letters}{new_number}"