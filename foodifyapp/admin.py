from django.contrib import admin

# Register your models here.
from foodifyapp.models import UserProfile, Menu, Restaurant, Statistics

admin.site.register(UserProfile)
admin.site.register(Menu)
admin.site.register(Restaurant)
admin.site.register(Statistics)