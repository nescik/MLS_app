from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm, EditUserForm, CustomPasswordChangeForm
from django.contrib.auth import authenticate
from django.contrib.auth.models import auth, User
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .models import Profile
from django.contrib import messages

def home(request):
    return render(request, 'main/home.html')


def sign_up(request):

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/home')
    else :
        form = RegisterForm()

    context = {"form":form}

    return render(request, 'registration/sign_up.html', context=context)


def my_login(request):
    form = LoginForm()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)

            profile = user.profile
            if not profile.is_profile_complete():
                messages.warning(request, 'Prosze uzupełnić dane (imię oraz nazwisko)!')
                return redirect('account-general')
            else:
                return redirect('home')
            
    context = {"form":form}

    return render(request, 'registration/login.html', context=context)


def user_logout(request):

    auth.logout(request)

    return redirect('my-login')

def user_profile(request):
    return render(request, 'user_profile/account_general.html')


def account_general(request):

    user = request.user
    form = EditUserForm(request.POST or None, request.FILES or None, instance=user)

    if request.method == 'POST':
        if form.is_valid():
            email_value = form.cleaned_data['email']
            existing_user = User.objects.filter(email = email_value).exclude(id=user.id).first()
            if existing_user:
                form.add_error('email', 'Istnieje użytkownik z podanym adresem email!')
            else:
                form.save()
                return redirect(account_general)
    profile = request.user.profile
    if not profile.is_profile_complete():
                messages.warning(request, 'Prosze uzupełnić dane (imię oraz nazwisko)!')

    contex = {'form':form}
    return render(request, 'user_profile/account_general.html', context=contex)


class PasswordsChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('account-general')



def account_change_password(request):

    return render(request, 'user_profile/account_change_password.html') 




def account_info(request):
    return render (request, 'user_profile/account_info.html')

def account_social(request):
    return render (request, 'user_profile/account_social.html')