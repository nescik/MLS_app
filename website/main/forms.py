from collections.abc import Mapping
from typing import Any
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.forms.widgets import PasswordInput, TextInput
from django.forms import ModelForm
from .models import Profile, Team, File
from django_countries.widgets import CountrySelectWidget

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','email', 'password1', 'password2']
    
    error_messages = {
        'password_mismatch': 'Podane hasła nie są identyczne!',
    }


    def clean_email(self): 
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Podany email juz istniej!')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Podana nazwa użytkownika już istnieje!')
        return username


    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Nazwa użytkownika'
        self.fields['password1'].label = 'Hasło'
        self.fields['password2'].label = 'Powtórz hasło'


class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.fields['username'].label = 'Nazwa użytkownika'
        self.fields['password'].label = 'Hasło'

class ProfileForm(ModelForm):
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
    
class EditInfoUserForm(ModelForm):
    class Meta:
        model = Profile

        fields = ['bio','country','age','phone_number','website']
        widgets = {'country':CountrySelectWidget()}

    
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=PasswordInput())
    new_password1 = forms.CharField(widget=PasswordInput())
    new_password2 = forms.CharField(widget=PasswordInput())

    class Meta:
        model = User
        fields = ['old_password','new_password1','new_password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

        self.fields['old_password'].label = 'Stare hasło'
        self.fields['new_password1'].label = 'Nowe hasło'
        self.fields['new_password2'].label = 'Powtórz hasło'

class CreateTeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'members']

class AddFileForm(ModelForm):
    class Meta:
        model = File
        fields = ['file', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['file'].label = 'Plik'
        self.fields['description'].label = 'Opis'

class AddNewMember(forms.Form):
    members = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        self.fields['members'].label = 'Użytkownicy'

        if team:
            existing_members = team.members.all()
            users_not_in_team = User.objects.exclude(id__in=[user.id for user in existing_members])
            self.fields['members'].queryset = users_not_in_team

            if not users_not_in_team:
                self.fields['members'].choices = [('', ('Brak użytkowników do dodania'))]