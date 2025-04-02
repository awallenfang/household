from django.contrib import admin

from shopping.models import ShoppingList, ShoppingItem, ShoppingItemOnList


# Register your models here.
class ShoppingItemOnListInline(admin.TabularInline):
    model = ShoppingItemOnList
    fields = ("item", "list", "checked", "bought_by", "amount")

@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    model = ShoppingItem

@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    model = ShoppingList
    inlines = (ShoppingItemOnListInline, )
