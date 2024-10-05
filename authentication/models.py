import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from core.models import TimeStampMixin
from .managers import UserManager


class User(AbstractUser):
    """
    User model with additional fields and custom validations.
    Attributes:
        email (EmailField): User's email address.
        username (CharField): User's username.
        is_superuser (BooleanField): Indicates whether the user is a superuser.
        is_staff (BooleanField): Indicates whether the user is a staff member.
        password (CharField): User's password.

    """
    email_validator = RegexValidator(
        regex=r"^[a-zA-Z0-9._%+-]+@gmail\.com$",
        message="enter a valid email"
    )
    username_validator = RegexValidator(
        regex=r'^.{8,}$',
        message='Username must be at least 8 characters long and contain at least one uppercase letter.',
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        validators=[email_validator]
    )

    username = models.CharField(
        verbose_name='username',
        max_length=30,
        unique=True,
        validators=[username_validator])

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4(), editable=False, unique=True)
    objects = UserManager()

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f'{self.username}---{self.email}'

    def save(self, *args, **kwargs):
        if self.is_superuser == False:
            if not self.pk:
                self.set_password(self.password)
        super().save(*args, **kwargs)


class SellerProfile(TimeStampMixin):
    """
    Seller profile model with additional fields.
    Attributes:
        user (OneToOneField): Foreign key to User model.
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
        company_name (CharField): User's company name.
        about_company (TextField): User's company description.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    company_name = models.CharField(max_length=50, null=True, blank=True, default='personal business')
    about_company = models.TextField(null=True, blank=True)
    expired_at = None
    is_blocked = models.BooleanField(default=False, null=True, blank=True)


class CustomerProfile(TimeStampMixin):
    """
    Customer profile model with additional fields.
    Attributes:
        user (OneToOneField): Foreign key to User model.
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
    """
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    expired_at = None


class Address(TimeStampMixin):
    """
    Address model with additional fields.
    Attributes:
        costumer (ForeignKey): Foreign key to User model.
        province (CharField): Province of the address.
        city (CharField): City of the address.
        street (CharField): Street of the address.
        alley (CharField): Alley of the address.
        house_number (CharField): House number of the address.
        full_address (TextField): Full address.
    """

    costumer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='costumer_address')
    province = models.CharField(max_length=25)
    city = models.CharField(max_length=30)
    street = models.CharField(max_length=250)
    alley = models.CharField(max_length=250)
    house_number = models.CharField(max_length=4)
    full_address = models.TextField(max_length=250)
    expired_at = None

    def __str__(self):
        return f"{self.province} {self.city}"
