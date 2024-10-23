from django.db import models

class NonDeletedObjects(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

