from django.db import models


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

