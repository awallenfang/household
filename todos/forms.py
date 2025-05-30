from django import forms

from hub.models import Profile
from todos.models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ["description", "name", "assigned_user"]
        
    def __init__(self, space=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        if space:
            self.fields["assigned_user"].queryset = Profile.objects.filter(spaces__in = [space])