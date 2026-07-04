from django import forms
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms import layout

from space.models import SharedSpace


class SpaceForm(forms.ModelForm):
    class Meta:
        model = SharedSpace
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.layout = layout.Layout(
            layout.Field("name", placeholder=_("Space name")),
        )
