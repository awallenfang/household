from django import forms
from django.utils import timezone


class NewTransactionForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    description = forms.CharField(max_length=500, required=False)
    amount = forms.DecimalField(max_digits=100, decimal_places=2, required=True)
    date = forms.SplitDateTimeField(required=True, initial=timezone.now)
    currency = forms.ChoiceField(choices=[("EUR", "EUR"), ("USD", "USD")], required=True)
    sender = forms.CharField(max_length=100, required=False)
    receiver = forms.CharField(max_length=100, required=False)
    tag = forms.CharField(max_length=100, required=False)