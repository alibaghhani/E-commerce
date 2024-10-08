from django.contrib import admin

# Register your models here.
from .models import (Product, Category, Image)
from authentication.models import (User, SellerProfile, CustomerProfile, Address)

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(User)
admin.site.register(SellerProfile)
admin.site.register(CustomerProfile)
admin.site.register(Address)
