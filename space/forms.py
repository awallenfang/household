from django import forms

from space.models import SharedSpace


class SpaceForm(forms.ModelForm):
    class Meta:
        model = SharedSpace
        fields = ["name"]