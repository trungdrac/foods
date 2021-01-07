from django.contrib import admin

# Register your models here.
from .models import User, Dish, Menu, Rating

admin.site.register((User, Dish, Menu, Rating))
