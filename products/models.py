import uuid

from django.contrib.auth import get_user_model

from authentication.models import SellerProfile, User
from django.core.validators import FileExtensionValidator
from django.db import models
from core.models import TimeStampMixin, SoftDelete
from slugify import slugify
user = get_user_model()

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
    slug = models.SlugField(unique=True, max_length=250)
    seller = models.ForeignKey(SellerProfile, on_delete=models.PROTECT, related_name='seller_product')

    expired_at = None

    def get_discounted_price(self):
        discounts = self.product_discount.all()
        discounted_price = self.price

        for discount in discounts:
            if discount.type_of_discount == 'percentage':
                discounted_price = self.price - (self.price * (discount.discount / 100))
            else:
                discounted_price -= discount.discount

        return discounted_price

    @property
    def discounted_price(self):
        return self.get_discounted_price()

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        text = f"{self.slug}{uuid.uuid4()}"
        self.slug = slugify(text)
        super(Product, self).save(*args, **kwargs)

    @property
    def discount_amount(self):
        for discount in self.product_discount.all():
            discount_amount = f"{discount.discount} {discount.type_of_discount}"
            return discount_amount

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


class Discount(TimeStampMixin):
    """
    discount model

    -----fields-----
    discount = models.PositiveIntegerField(max_length=250, blank=True, null=True, unique=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_discount')


    """
    DISCOUNT_CHOICES = (
        ('percentage', '%'),
        ('cash', '$')
    )
    type_of_discount = models.CharField(choices=DISCOUNT_CHOICES, max_length=250, null=True, blank=True)
    discount = models.PositiveIntegerField(blank=True, null=True, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_discount')
