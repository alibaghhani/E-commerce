from authentication.models import User, CustomerProfile, SellerProfile
from rest_framework import serializers


class CustomerProfileSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=50, required=True)
    username = serializers.CharField(max_length=50, required=True)
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        username = validated_data.pop('username')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        CustomerProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name
        )

        return user


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ('first_name', 'last_name', 'company_name', 'about_company')
