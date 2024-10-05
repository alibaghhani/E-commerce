from django.core.validators import FileExtensionValidator
from django.db import models
from core.models import TimeStampMixin


class Product(TimeStampMixin):
    """
    Product model for save products.
    Attributes:
        name (CharField): Product name.
        price (PositiveIntegerField): Product price.
        detail (TextField): Product description.
        category (ForeignKey): Foreign key to Category model.
        warehouse (PositiveIntegerField): Product warehouse number.
        slug (SlugField): Product slug.
    """
    name = models.CharField(max_length=250)
    price = models.PositiveIntegerField()
    detail = models.TextField(max_length=250)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='product_category')
    warehouse = models.PositiveIntegerField(null=True, blank=True)
    slug = models.SlugField(unique=True)

    expired_at = None

