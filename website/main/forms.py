from collections.abc import Mapping
from typing import Any
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput
from django.forms import ModelForm
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','email', 'password1', 'password2']
    
        
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Nazwa użytkownika'
        self.fields['password1'].label = 'Hasło'
        self.fields['password2'].label = 'Powtórz hasło'


class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())

    def __init__(self, request: Any = ..., *args: Any, **kwargs: Any) -> None:
        super().__init__(request, *args, **kwargs)

        self.fields['username'].label = 'Nazwa użytkownika'
        self.fields['password'].label = 'Hasło'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class EditUserForm(ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['image'] = ProfileForm().fields['image']

        self.fields['username'].label = 'Nazwa użytkownika'
        self.fields['first_name'].label = 'Imię'
        self.fields['last_name'].label = 'Nazwisko'
        self.fields['image'].label = 'Zmień zdjęcie'
    
    def save(self, commit=True):
        user = super().save(commit)
        profile = user.profile

        if 'image' in self.files:
            profile.image = self.files['image']
            profile.save()

        return user