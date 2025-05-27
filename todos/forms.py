from django import forms

from hub.models import Profile
from todos.models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ["description", "name", "assigned_user"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["assigned_user"].queryset = Profile.objects.filter(space__contains = self.instance.space)