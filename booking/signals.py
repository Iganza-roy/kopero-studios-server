from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review, CrewMember

@receiver(post_save, sender=Review)
def update_average_rating_on_create_or_update(sender, instance, **kwargs):
    update_average_rating(instance.crew_member)

@receiver(post_delete, sender=Review)
def update_average_rating_on_delete(sender, instance, **kwargs):
    update_average_rating(instance.crew_member)

def update_average_rating(crew_member):
    # Get all reviews for the specified crew member
    reviews = Review.objects.filter(crew_member=crew_member)
    
    # Calculate the average rating
    if reviews.exists():
        average = reviews.aggregate(models.Avg('rating'))['rating__avg']
        crew_member.average_rating = average or 0
    else:
        crew_member.average_rating = 0
    crew_member.save()
