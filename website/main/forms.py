from collections.abc import Mapping
from typing import Any
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.forms.widgets import PasswordInput, TextInput
from django.forms import ModelForm
from .models import Profile, Team, File, TeamMembership
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
    members = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_superuser=False))
    class Meta:
        model = Team
        fields = ['name', 'members']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['name'].label = 'Nazwa'
        self.fields['members'].label = 'Członkowie'



class AddFileForm(ModelForm):
    class Meta:
        model = File
        fields = ['file', 'description', 'privacy_level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['file'].label = 'Plik'
        self.fields['description'].label = 'Opis'
        self.fields['privacy_level'].label = 'Poziom tajności'

class EditFileForm(ModelForm):
    class Meta:
        model = File
        fields = ['file', 'description']

class AddNewMember(forms.Form):
    members = forms.ModelChoiceField(queryset=User.objects.all())
    groups = forms.ModelChoiceField(queryset=Group.objects.all())

    def __init__(self, *args, **kwargs):
        team = kwargs.pop('team', None)
        super().__init__(*args, **kwargs)
        self.fields['members'].label = 'Użytkownicy'
        self.fields['groups'].label = 'Grupa'

        if team:
            existing_members = team.members.all()
            users_not_in_team = User.objects.filter(is_superuser=False).exclude(id__in=[user.id for user in existing_members])
            self.fields['members'].queryset = users_not_in_team

            if not users_not_in_team:
                self.fields['members'].choices = [('', ('Brak użytkowników do dodania'))]
    


class EditUserPermission(ModelForm):

    groups = forms.ModelChoiceField(queryset=Group.objects.all())
    class Meta:
        model = TeamMembership
        fields = ['groups']
    
        
    full_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    def __init__(self, team, user, *args, **kwargs):
        super(EditUserPermission, self).__init__(*args, **kwargs)
        team_membership = TeamMembership.objects.filter(user=user, team=team).first()
        self.fields['groups'].initial = team_membership.groups.first().id if team_membership and team_membership.groups.exists() else None
        self.fields['groups'].label = 'Grupa'
        self.fields['full_name'].initial = user.get_full_name
