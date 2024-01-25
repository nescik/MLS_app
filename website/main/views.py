from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm, EditUserForm, CustomPasswordChangeForm, EditInfoUserForm, CreateTeamForm, AddFileForm, AddNewMember
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import auth, User
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Team, File
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def home(request):
    teams = Team.objects.all()
    user = request.user

    if request.method == 'POST':
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            founder = request.user
            team = form.save(commit=False)
            team.founder = founder
            team.save() 

            members = form.cleaned_data['members']
            team.members.set(members)
            team.members.add(founder)
            
            return redirect('home')
    else:
        form = CreateTeamForm()

    context = {'teams':teams, 'form':form, 'user':user}
    return render(request, 'main/home.html', context=context)


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
            login(request, user)

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



@login_required
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
                messages.success(request, 'Informacje zostały zauktualizowane')
                return redirect(account_general)
    profile = request.user.profile
    if not profile.is_profile_complete():
                messages.warning(request, 'Prosze uzupełnić imię oraz nazwisko!')

    contex = {'form':form}
    return render(request, 'user_profile/account_general.html', context=contex)


class PasswordsChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('account-change-password')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Hasło zostało zmienione pomyślnie')
        return response        
    
@login_required
def account_change_password(request):

    return render(request, 'user_profile/account_change_password.html') 

@login_required
def account_info(request):
    profile = request.user.profile
    form = EditInfoUserForm(request.POST or None, instance=profile)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Informacje zostały zauktualizowane')
            return redirect ('account-info')

    context = {'form':form}
    return render (request, 'user_profile/account_info.html', context=context)

def account_social(request):
    return render (request, 'user_profile/account_social.html')

@login_required
def team_detail(request, id):

    team = get_object_or_404(Team, pk=id)

    if request.user.is_authenticated:
        user = request.user

    context = {'team':team, 'user':user}

    return render(request, 'teams/team_files.html', context=context)

@login_required
def team_files(request, id):
    team = get_object_or_404(Team, pk=id)

    files = File.objects.filter(team=team)

    context = {'team':team,  'files':files}
    return render(request, 'teams/team_files.html', context=context)

@login_required
def download_file(request,id):
    file_instance = get_object_or_404(File, pk=id)
    return file_instance.download(request)

@login_required
def team_add_file(request, id):
    team = get_object_or_404(Team, pk=id)
    user = request.user
    user_files = File.objects.filter(team=team, author=user)

    if request.method == 'POST':
        form = AddFileForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            file = form.save(commit=False)
            file.team = team
            file.author = user
            file.save()
            return redirect('team_files', id=team.id)
    else:
        form = AddFileForm()

    context = {'team':team, 'form':form, 'user_files':user_files}
    return render(request, 'teams/team_add_file.html', context=context)

@login_required
def team_permission(request, id):
    team = get_object_or_404(Team, pk=id)

    context = {'team':team}
    return render(request, 'teams/team_permission.html', context=context)

@login_required
def team_add_member(request, id):
    team = get_object_or_404(Team, pk=id)

    if request.method == 'POST':
        form = AddNewMember(request.POST or None, team=team)
        if form.is_valid():
            member = form.cleaned_data['members']
            team.members.add(member)
            return redirect('team_members', id=team.id)
    else:
        form = AddNewMember(team=team)
        form.team = team 

    context = {'team':team, 'form':form}
    return render(request, 'teams/team_members.html', context=context)

@login_required
def remove_member(request, team_id, member_id):
    team = get_object_or_404(Team, id = team_id)
    member = get_object_or_404(User, id=member_id)

    team.members.remove(member)

    return redirect('team_members', id=team.id)