import random
import uuid
from django.utils.text import slugify
from authentication.models import User, SellerProfile
from authentication.models import *
from order.models import *
from products.models import *
# Create Categories
categories = []
for i in range(20):
    categories.append(Category(name=f"Category {i + 1}"))
Category.objects.bulk_create(categories)

# Create Users
users = []
for i in range(100):
    users.append(User(
        username=f"user_{i + 1}",
        email=f"user_{i + 1}@gmail.com",
        password='password123',  # Set a default password for simplicity
        is_staff=False,
        is_superuser=False
    ))
User.objects.bulk_create(users)

# Create Seller Profiles
seller_profiles = []
for user in users[:20]:  # Assign SellerProfile to the first 20 users
    seller_profiles.append(SellerProfile(
        user=user,
        first_name=f"FirstName_{user.username}",
        last_name=f"LastName_{user.username}",
        company_name=f"Company_{user.username}",
        about_company=f"About {user.username}"
    ))
SellerProfile.objects.bulk_create(seller_profiles)

# Create Discount Codes
discount_codes = []
for i in range(100):
    discount_codes.append(DiscountCode(
        code=f"DIST_CODE_{i + 1}",
        type_of_discount=random.choice(['percentage', 'cash']),
        discount=random.randint(1, 50),  # Random discount between 1 and 50
        user=random.choice(users)
    ))
DiscountCode.objects.bulk_create(discount_codes)

# Create Products
products = []
categories = list(Category.objects.all())  # Get all categories
for i in range(100):
    products.append(Product(
        name=f"Product {i + 1}",
        price=random.randint(1000, 10000),  # Random price between 1000 and 10000
        detail=f"This is a description for product {i + 1}.",
        category=random.choice(categories),
        warehouse=random.randint(1, 100),  # Random warehouse number between 1 and 100
        slug=slugify(f"product-{i + 1}-{uuid.uuid4()}"),
        seller=random.choice(seller_profiles)  # Random seller profile
    ))
Product.objects.bulk_create(products)

# Create Addresses for users
addresses = []
for user in users:
    addresses.append(Address(
        costumer=user,
        province="Province A",
        city="City B",
        street="Street C",
        alley="Alley D",
        house_number=str(random.randint(1, 100)),
        full_address=f"{user.username}'s Full Address"
    ))
Address.objects.bulk_create(addresses)

print('Successfully created sample data.')