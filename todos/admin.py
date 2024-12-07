from django.contrib import admin

from .models import OrderedUser, Todo, TodoRecurrency

admin.site.register(Todo)


class OrderedUserInline(admin.TabularInline):
    model = OrderedUser
    fields = ("user", "order" ,"empty")

class RecurrencyAdmin(admin.ModelAdmin):
    model = TodoRecurrency
    inlines = (OrderedUserInline, )

admin.site.register(TodoRecurrency, RecurrencyAdmin)