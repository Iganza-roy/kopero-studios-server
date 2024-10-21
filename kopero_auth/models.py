from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from django.core.mail import send_mail
from uuid import uuid4 as uuid
from django.utils.translation import gettext_lazy as _


# Create your models here.

class MyUserManager(BaseUserManager):
    def _create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, username, password, **extra_fields):
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email=None, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, username, password, **extra_fields)
    
class BaseUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid, primary_key=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True, unique=True)
    username = models.CharField(_("username"), max_length=150, blank=True, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(max_length=1000, blank=True)
    is_ops_admin = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
        ),
    )

    is_staff = models.BooleanField(
        _("staff"),
        default=False,
        help_text=_(
            "Designates whether this user is staff or not. "
        ),
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = MyUserManager()

    MAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def _usable(self):
        return self.has_usable_password()

    _usable.boolean = True
    usable = property(_usable)

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sends an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class ClientManager(MyUserManager):
    def create_client(self, email, username, password=None, **extra_fields):
        return self.create_user(email, username, password, **extra_fields)


class Client(BaseUser):
    bookings = models.JSONField(default=list, blank=True, null=True)

    objects = ClientManager()

    def __str__(self):
        return self.get_full_name()
    class Meta:
        db_table = "clients"
        ordering = ["-date_joined"]


class CrewMemberManager(MyUserManager):
    def create_crew(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        return self.create_user(email, username, password, **extra_fields)


class CrewMember(BaseUser):
    PHOTOGRAPHER = 'photographer'
    VIDEOGRAPHER = 'videographer'
    
    CATEGORY_CHOICES = [
        (PHOTOGRAPHER, 'Photographer'),
        (VIDEOGRAPHER, 'Videographer'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    sessions_booked = models.JSONField(default=list, blank=True, null=True)

    objects = CrewMemberManager()

    def __str__(self):
        return self.get_full_name()
    class Meta:
        db_table = "crew"
        ordering = ["-date_joined"]
