from django import forms

from hub.models import Profile
from todos.models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ["description", "name", "assigned_user"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields["assigned_user"].queryset = Profile.objects.filter(spaces__in = [self.instance.space])
        self.fields["description"].required = False