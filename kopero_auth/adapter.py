from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http.response import HttpResponseRedirect
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from allauth.account.utils import user_email, user_field, get_user_model
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom Adapter that overrides the send_confirmation_mail method to add custom context
    """

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        data = form.cleaned_data
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        username = data.get('username')
        phone = data.get('phone')
        user_email(user, email)
        if first_name:
            user_field(user, 'first_name', first_name)
        if last_name:
            user_field(user, 'last_name', last_name)
        if phone:
            user_field(user, 'phone', phone)
        if username:
            user_field(user, 'username', username)
        else:
            pass
        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user

    def clean_email(self, email):
        """
        Normalize the email address by lowercasing it.
        """
        try:
            email = email.lower()
        except ValueError:
            pass
        return email

    def respond_email_verification_sent(self, request, user):
        return HttpResponseRedirect(reverse("auth:account_email_verification_sent"))