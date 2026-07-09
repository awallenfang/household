from django import forms

from hub.models import Profile
from todos.models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ["description", "name", "assigned_user"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control form-control-sm"}),
            "description": forms.Textarea(attrs={"class": "form-control form-control-sm", "rows": 4}),
            "assigned_user": forms.Select(attrs={"class": "form-select form-select-sm"}),
        }
        
    def __init__(self, *args, space=None,  **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        if space:
            self.fields["assigned_user"].queryset = Profile.objects.filter(spaces__in = [space])