from django.db import models

from root import settings

class Recipient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}'

def get_currencies():
    return {curr: curr for curr in settings.CURRENCIES}

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, null=True, blank=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2)
    currency = models.CharField(max_length=3, choices=get_currencies, default="EUR")
    date = models.DateTimeField(blank=True, null=True)
    sender = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='sender', null=True, blank=True)
    receiver = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='receiver', null=True, blank=True)

    def __str__(self):
        return f'{self.name}: {self.amount} {self.currency}'
    
class Tag(models.Model):
    tag = models.CharField(max_length=100)
    colour = models.CharField(max_length=7)

    def __str__(self):
        return f'{self.tag}'
    
def get_all_tags():
    return {tag.tag:tag.tag for tag in Tag.objects.all()}

class TransactionToTag(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.transaction.name} - {self.tag.tag}'