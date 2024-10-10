from django.db import models
from booking.models import AvailableTime
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils import timezone
from django.core.mail import send_mail
from uuid import uuid4 as uuid
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from common.models import TimeStampedModelMixin


# Create your models here.

class MyUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid, primary_key=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True, unique=True)
    username = models.CharField(_("username"), max_length=150, blank=True, unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    is_ops_admin = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    modified_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="deleted_%(class)s",
    )
    OPERATIONS_ADMIN = "operations"
    REGULAR = 'regular'
    PHOTOGRAPHER = 'photographer'
    ROLE_CHOICES = (
        ("PHOTOGRAPHER", "photographer"),
        ("REGULAR", "regular"),
        (OPERATIONS_ADMIN, "Operations Admin"),
    )
    role = models.CharField(
        _("user role"),
        max_length=20,
        blank=True,
        choices=ROLE_CHOICES,
        help_text=_(
            "Designates the role of the user in the system - For Authorization"
        ),
        default="Regular"
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = MyUserManager()

    MAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

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

    def _is_regular_user(self):
        """Returns whether a user is regular or not"""
        return self.role == self.REGULAR

    _is_regular_user.boolean = True
    is_regular_user = property(_is_regular_user)

    def _is_photographer(self):
        """Returns whether a user is photographer or not"""
        return self.role == self.PHOTOGRAPHER

    _is_photographer.boolean = True
    is_photographer = property(_is_photographer)


    # def _is_ops_admin(self):
    #     return self.role == self.OPERATIONS_ADMIN

    # _is_ops_admin.boolean = True
    # is_ops_admin = property(_is_ops_admin)

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]
        constraints = [
            models.UniqueConstraint(fields=['username', 'email'], name='unique_username_email')
        ]

class Profile(TimeStampedModelMixin):
    """
    A user profile instance - stores extra information about a user instance
    - user: The user object to which this profile belongs
    - picture: URL to the user's profile picture
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        on_delete=models.CASCADE,
    )
    picture = models.URLField(blank=True)
    address = models.CharField(max_length=250,blank=True)
    town = models.CharField(max_length=250,blank=True)

    portfolio_link = models.URLField(blank=True, null=True)
    available_time = models.ManyToManyField(AvailableTime)

    def __str__(self):
        return self.user.get_username()
