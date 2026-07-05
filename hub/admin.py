from django.contrib import admin

from space.models import SharedSpace

from .models import Profile

admin.site.register(Profile)
admin.site.register(SharedSpace)
