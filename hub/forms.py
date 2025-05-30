from django import forms
from django.utils.translation import gettext_lazy as _

class LoginForm(forms.Form):
    template_name = "hub/form_template.html"
    username = forms.CharField(label=_("Username"), max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class SignupForm(forms.Form):
    template_name = "hub/form_template.html"
    username = forms.CharField(label=_("Username"), max_length=100, 
                               widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(label=_("Email Address"), widget=forms.TextInput(attrs={'placeholder': 'E-Mail'}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    repeat_password = forms.CharField(label=_("Repeat password"), widget=forms.PasswordInput(
                                                    attrs={'placeholder': 'Repeat Password'}
                                                    ))