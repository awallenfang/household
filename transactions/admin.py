from django.contrib import admin

from .models import Transaction, Recipient, Tag, TransactionTag

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Recipient)
admin.site.register(Tag)
admin.site.register(TransactionTag)