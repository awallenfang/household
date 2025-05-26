from django.db import models
from django.db.models import CASCADE

from space.models import SharedSpace


# Create your models here.

class ShoppingItem(models.Model):
    name = models.CharField(verbose_name="Name", max_length=100)
    price = models.DecimalField(verbose_name="Price", decimal_places=2, max_digits=8)
    space = models.ForeignKey(SharedSpace, on_delete=CASCADE, verbose_name="Space")

    def __str__(self):
        return f'{self.name} | {self.price}'


class ShoppingList(models.Model):
    items = models.ManyToManyField(ShoppingItem, verbose_name="Items", through="ShoppingItemOnList")
    space = models.ForeignKey(SharedSpace, on_delete=CASCADE, verbose_name="Space")

class ShoppingItemOnList(models.Model):
    item = models.ForeignKey(ShoppingItem, on_delete=CASCADE)
    list = models.ForeignKey(ShoppingList, on_delete=CASCADE)
    amount = models.PositiveIntegerField(verbose_name="Amount", default=1)
    checked = models.BooleanField(verbose_name="Bought", default=False)
    bought_by = models.ForeignKey("hub.Profile", null=True, blank=True, on_delete=CASCADE)

