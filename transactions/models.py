from django.db import models

from root import settings

# Create your models here.

def get_currencies():
    return {curr: curr for curr in settings.CURRENCIES}

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    currency = models.CharField(max_length=3, choices=get_currencies, default="EUR")
    date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}: {self.amount} {self.currency}'