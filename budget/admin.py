from django.contrib import admin
from .models import BudgetWeekList, BudgetWeekListItem


# Register your models here.

class WeekListInline(admin.TabularInline):
    model = BudgetWeekListItem
    fields = ("title", "cost" ,"cleared", "paid_by")

class BudgetWeekAdmin(admin.ModelAdmin):
    model = BudgetWeekList
    inlines = (WeekListInline, )

admin.site.register(BudgetWeekList, BudgetWeekAdmin)