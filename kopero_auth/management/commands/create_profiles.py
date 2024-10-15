# kopero_auth/management/commands/create_profiles.py
from django.core.management.base import BaseCommand
from kopero_auth.models import User, Profile

class Command(BaseCommand):
    help = 'Create profiles for users without profiles'

    def handle(self, *args, **kwargs):
        users_without_profiles = User.objects.filter(profile__isnull=True)
        for user in users_without_profiles:
            Profile.objects.create(user=user, created_by=user)
            self.stdout.write(self.style.SUCCESS(f'Created profile for user {user.id}'))