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
        message='لطفا یک ایمیل درست وارد کنید'
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
    objects = UserManager()

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f'{self.username}---{self.email}'

    def save(self, *args, **kwargs):
        if self.is_superuser == False:
            if not self.pk:
                self.set_password(self.password)
        super().save(*args, **kwargs)
