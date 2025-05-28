from django.contrib import admin

from .models import OrderedUser, Todo, TodoSchedule

admin.site.register(Todo)


class OrderedUserInline(admin.TabularInline):
    model = OrderedUser
    fields = ("user", "order" ,"empty")

class ScheduleAdmin(admin.ModelAdmin):
    model = TodoSchedule
    inlines = (OrderedUserInline, )

admin.site.register(TodoSchedule, ScheduleAdmin)