from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        active_users = UserModel._default_manager.filter(email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())
