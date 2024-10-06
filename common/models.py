from django.conf import settings
from django.db import models
import uuid

class TimeStampedModelMixin(models.Model):
    """
    This abstract model contains shared functionality pertaining to
    timestamp fields in a model.
    These fields are:
    - created_at: this gives the timestamp when an object is created.
    - updated_at: this gives the timestamp when an object is last updated.
    - created_by: this is a foreign key to the user who created the object.
    - modified_by: this is a foreign key to the user who last modified the object.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_%(class)s",
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="modified_%(class)s",
    )

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["-created_at"])]

    def __str__(self):
        if hasattr(self, "name"):
            return self.name
        return str(self.id)

class FlaggedModelMixin(models.Model):
    """
    This abstract model contains shared functionality pertaining to
    flag-enabled fields in a model.
    These fields are:
    - is_deleted: this is marks the model instance as deleted, instead of
    physically deleting.
    - deleted_at: this goes hand in hand with `is_deleted`.
    Gives the timestamp when an object is marked as deleted.
    - is_active: this is marks the instance as active
    """

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_deleted"]),
        ]
