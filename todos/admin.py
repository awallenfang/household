from django.contrib import admin

from .models import OrderedUser, Todo, TodoRecurrency

admin.site.register(Todo)
admin.site.register(OrderedUser)
admin.site.register(TodoRecurrency)