import uuid
from authentication.models import SellerProfile
from django.core.validators import FileExtensionValidator
from django.db import models
from core.models import TimeStampMixin,SoftDelete
from slugify import slugify


class Product(TimeStampMixin, SoftDelete):
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
    seller = models.ForeignKey(SellerProfile, on_delete=models.PROTECT, related_name='seller_product')

    expired_at = None

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        text = f"{self.slug}{uuid.uuid4()}"
        self.slug = slugify(text)
        super(Product, self).save(*args, **kwargs)

    class Meta:
        ordering = ('price',)


class Category(TimeStampMixin):
    """
    Category model for save product categories.
    Attributes:
        name (CharField): Category name.
        parent (ForeignKey): Foreign key to Category model.
        expired_at (DateTimeField): Timestamp for expiration.
    """
    name = models.CharField(max_length=250)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="child")
    expired_at = None

    def get_all_parents(self):
        return Category.objects.filter(parent_id=None)

    def __str__(self):
        return f"{self.name}"


class Image(TimeStampMixin, SoftDelete):
    image = models.ImageField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpeg", "png", "jpg", "gif", "mp4", "avi", "flv"]
            )
        ],
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products_post')
