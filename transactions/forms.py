from django import forms
from django.utils import timezone

from .models import get_currencies


class NewTransactionForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    description = forms.CharField(max_length=500, required=False)
    amount = forms.DecimalField(max_digits=100, decimal_places=2, required=True)
    date = forms.SplitDateTimeField(required=True, initial=timezone.now())
    currency = forms.ChoiceField(choices=get_currencies, required=True)