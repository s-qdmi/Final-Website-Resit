from django.contrib import admin
from .models import Category, Item, Review, Profile, CartItem

admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Review)
admin.site.register(Profile)
admin.site.register(CartItem)
