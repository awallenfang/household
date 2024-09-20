from django import forms


class LoginForm(forms.Form):
    template_name = "hub/form_template.html"
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class SignupForm(forms.Form):
    template_name = "hub/form_template.html"
    username = forms.CharField(max_length=100, 
                               widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'E-Mail'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    repeat_password = forms.CharField(widget=forms.PasswordInput(
                                                    attrs={'placeholder': 'Repeat Password'}
                                                    ))