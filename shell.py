import os
import django
import random
import uuid
from faker import Faker
from slugify import slugify

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # Replace 'myproject' with your project name
django.setup()

# Import models
from authentication.models import User, SellerProfile, CustomerProfile, Address
from products.models import Product, Category, Image
from order.models import Basket
from core.models import TimeStampMixin
from django.contrib.auth.hashers import make_password

# Initialize faker instance
fake = Faker()


def create_users():
    print("Creating users...")
    users = []
    for _ in range(100):
        user = User.objects.create(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password=make_password("password123"),
            is_superuser=False,
            is_staff=False,
            is_seller=random.choice([True, False]),
            uuid=uuid.uuid4()
        )
        users.append(user)
    print("Users created.")
    return users


def create_seller_profiles(users):
    print("Creating seller profiles...")
    sellers = [user for user in users if user.is_seller]
    seller_profiles = []
    for user in sellers:
        seller_profile = SellerProfile.objects.create(
            user=user,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            company_name=fake.company(),
            about_company=fake.paragraph()
        )
        seller_profiles.append(seller_profile)
    print("Seller profiles created.")
    return seller_profiles


def create_customer_profiles(users):
    print("Creating customer profiles...")
    customers = [user for user in users if not user.is_seller]
    customer_profiles = []
    for user in customers:
        customer_profile = CustomerProfile.objects.create(
            user=user,
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        customer_profiles.append(customer_profile)
    print("Customer profiles created.")
    return customer_profiles


def create_categories():
    print("Creating categories...")
    categories = []
    for _ in range(10):
        category = Category.objects.create(
            name=fake.word(),
            parent=None  # Add parent relationships if needed
        )
        categories.append(category)
    print("Categories created.")
    return categories


def create_products(seller_profiles, categories):
    print("Creating products...")
    products = []
    for _ in range(100):
        product = Product.objects.create(
            name=fake.word(),
            price=random.randint(10, 1000),
            detail=fake.paragraph(),
            category=random.choice(categories),
            warehouse=random.randint(1, 100),
            slug=slugify(fake.unique.word()),
            seller=random.choice(seller_profiles)
        )
        products.append(product)
    print("Products created.")
    return products


def create_images(products):
    print("Creating images for products...")
    for product in products:
        Image.objects.create(
            product=product,
            image=fake.image_url()  # Use actual images if needed; adjust this as per your setup.
        )
    print("Images created.")


def create_baskets(customer_profiles, products):
    print("Creating baskets...")
    for customer in customer_profiles:
        basket = Basket.objects.create(
            customer=customer,
            products_list=[random.choice(products).id for _ in range(random.randint(1, 5))],
            quantity=random.randint(1, 10),
            product=random.choice(products)
        )
    print("Baskets created.")


def create_addresses(users):
    print("Creating addresses...")
    for user in users:
        Address.objects.create(
            costumer=user,
            province=fake.state(),
            city=fake.city(),
            street=fake.street_name(),
            alley=fake.street_address(),
            house_number=str(random.randint(1, 9999)),
            full_address=fake.address()
        )
    print("Addresses created.")


def main():
    users = create_users()
    seller_profiles = create_seller_profiles(users)
    customer_profiles = create_customer_profiles(users)
    categories = create_categories()
    products = create_products(seller_profiles, categories)
    create_images(products)
    create_baskets(customer_profiles, products)
    create_addresses(users)
    print("Dummy data generation completed.")


if __name__ == '__main__':
    main()
