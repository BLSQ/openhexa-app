from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User

# We won't be using the Django group feature
admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass
