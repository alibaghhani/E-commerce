from django.core.validators import RegexValidator

from authentication.models import User, CustomerProfile, SellerProfile
from rest_framework import serializers
from core.validator import email_validator, username_validator


class CustomerProfileSerializer(serializers.Serializer):
    """
    Customer profile serializer.
    Attributes:
        user (OneToOneField): Foreign key to User model.
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
    """
    email = serializers.EmailField(max_length=50, required=True, validators=[email_validator])
    username = serializers.CharField(max_length=50, required=True, validators=[username_validator])
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def create(self, validated_data):
        """
            Creates and saves a new User and CustomerProfile.
        """
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')

        user = User.objects.create(
            username=username,
            email=email,
            password=password
        )

        CustomerProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name
        )

        return {
            "username": user.username,
            "email": user.email,
            "first_name": user.customer_profile.first_name,
            "last_name": user.customer_profile.last_name
        }


class SellerProfileSerializer(serializers.Serializer):
    """
    Seller profile serializer.
    Attributes:
        user (OneToOneField): Foreign key to User model.
        first_name (CharField): User's first name.
        last_name (CharField): User's last name.
        company_name (CharField): User's company name.
        about_company (CharField): User's company description.

    """

    email = serializers.EmailField(required=True, validators=[email_validator])
    username = serializers.CharField(max_length=50, required=True, validators=[username_validator])
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    company_name = serializers.CharField(required=True)
    about_company = serializers.CharField(required=True)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def create(self, validated_data):
        """
        Create and return a new User instance, given the validated data.
        """
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        company_name = validated_data.pop('company_name')
        about_company = validated_data.pop('about_company')

        user = User.objects.create(
            username=username,
            email=email,
            password=password,
            is_seller=True
        )

        SellerProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            about_company=about_company

        )

        return {
            "username": user.username,
            "email": user.email,
            "first_name": user.seller_profile.first_name,
            "last_name": user.seller_profile.last_name,
            "company_name": user.seller_profile.company_name,
            "about_company": user.seller_profile.about_company
        }
