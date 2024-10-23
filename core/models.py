from django.db import models
from .managers import NonDeletedObjects

class TimeStampMixin(models.Model):
    """
    A base model with fields for creation, update, and expiration timestamps.
    Attributes:
        created_at (DateTimeField): Timestamp for creation.
        updated_at (DateTimeField): Timestamp for last update.
        expired_at (DateTimeField): Timestamp for expiration.
    """

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    expired_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class SoftDelete(models.Model):
    is_deleted = models.BooleanField(default=False)
    everything = models.Manager()
    objects = NonDeletedObjects()

    def soft_deleted(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        abstract = True
