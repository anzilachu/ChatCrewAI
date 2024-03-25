from django import forms
from django.contrib.auth.models import User

class CustomUserCreationForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

    def save(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password1")
        User.objects.create_user(username=username, password=password)
