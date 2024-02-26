import os
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, LoginForm, EditUserForm, CustomPasswordChangeForm, EditInfoUserForm, CreateTeamForm, AddFileForm, AddNewMember, EditFileForm, EditUserPermission
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import auth, User
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Team, File, TeamMembership
from django.contrib.auth.decorators import login_required, permission_required
from .permission_tools import check_perms
from django.db.models import Q



@login_required
def home(request):
    teams = Team.objects.all()
    user = request.user

    if request.method == 'POST':
        form = CreateTeamForm(request.POST, user=user)
        if form.is_valid():
            founder = request.user
            team = form.save(commit=False)
            team.founder = founder
            team.save() 

            TeamMembership.objects.create(user=founder, team=team)

            members = form.cleaned_data['members']
            for member in members:
                TeamMembership.objects.create(user=member, team=team)
            
            return redirect('home')
    else:
        form = CreateTeamForm(user=user)

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
    failed_attempts_key = 'failed_attempts'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                
                profile = user.profile
                if not profile.is_profile_complete():
                    return redirect('account-general')
                else:
                    request.session[failed_attempts_key] = 0
                    return redirect('home')
            else:
                messages.warning(request, 'Konto zablokowane! W celu odblokowania skontaktuj sie z administratorem')
        else:
            user_session_key = f'{failed_attempts_key}_{username}'

            failed_attempts = request.session.get(user_session_key, 0)
            failed_attempts += 1
            request.session[user_session_key] = failed_attempts

            
            if failed_attempts > 5:
                user_to_lock = get_object_or_404(User, username=username)
                user_to_lock.is_active = False
                user_to_lock.save()

                request.session[f'locked_account_{username}'] = True
                messages.error(request, 'Przekroczono liczbę nieudanych prób logowania. Konto zostało zablokowane! W celu odblokowania skontaktuj sie z administratorem')
            else:
                messages.warning(request, f'Nieudane logowanie! Po przekroczeniu 5 prób konto zostanie zablokowane. Próba {failed_attempts}')
                
            
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

def get_team_and_members(id):
    team = get_object_or_404(Team, pk=id)
    members = team.get_members()

    return team, members


@login_required
def team_files(request, id):
    team, members = get_team_and_members(id)
    

    if request.user.is_authenticated:
        user = request.user
    
    files = File.objects.filter(
        team=team,
        privacy_level__in=['public', 'confidencial', 'secret']
    ).filter(
        (Q(privacy_level='public')) | 
        (Q(privacy_level='confidencial') & check_perms(user, team, 'view_confidencial')) | 
        (Q(privacy_level='secret') & check_perms(user, team, 'view_secret'))
)


    if request.method == 'POST':
        file_id = request.POST.get('file-id')
        file = File.objects.filter(id=file_id).first()
        if file and file.author == request.user:
            file.delete()
            redirect('team_files', id=team.id)

    context = {'team': team, 'files': files, 'user':user, 'members': members, 'user':user}
    return render(request, 'teams/team_files.html', context=context)

@login_required
def edit_file(request, team_id, file_id):
    team, members = get_team_and_members(team_id)
    file = get_object_or_404(File, pk=file_id)
    privacy_level = file.privacy_level
    form = EditFileForm(request.POST or None, instance=file)
   
    if request.user.is_authenticated:
        user = request.user

    if request.method == 'POST':
        form = EditFileForm(request.POST, request.FILES, instance=file)
        if form.is_valid():
            form.save(commit=False)
            
            file.last_editor = request.user
            file.version += 1
            file.save()

            return redirect('team_files', id=team.id)
    else:
        form = EditFileForm( instance=file)


    context = {'team':team, 'form':form, 'members': members, 'user':user}

    if(
        (privacy_level == 'public' and check_perms(user, team, 'change_file')) or
        (privacy_level == 'confidencial' and check_perms(user, team, 'edit_confidencial')) or
        (privacy_level == 'secret' and check_perms(user, team, 'edit_secret'))
    ):    
        return render(request, 'teams/edit_file.html', context=context)
    else:
        raise Http404("Nie masz uprawnień do edycji tego pliku.")

@login_required
def download_file(request,id):
    file_instance = get_object_or_404(File, pk=id)

    privacy_level = file_instance.privacy_level
    user = request.user
    team = file_instance.team
    
    if (
        (privacy_level == 'public' and check_perms(user, team, 'download_file')) or
        (privacy_level == 'confidencial' and check_perms(user, team, 'download_confidencial')) or
        (privacy_level == 'secret' and check_perms(user, team, 'download_secret')) or
        (file_instance.author == user)
    ):
        return file_instance.download(request)
    


    raise Http404("Nie masz uprawnień do pobrania tego pliku.")

@login_required
def team_add_file(request, id):
    team, members = get_team_and_members(id)
    user = request.user
    user_files = File.objects.filter(team=team, author=user)

    if request.user.is_authenticated:
        user = request.user

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

    context = {'team':team, 'form':form, 'user_files':user_files, 'members': members, 'user':user}
    return render(request, 'teams/team_add_file.html', context=context)



@login_required
def team_permission(request, id):
    team, members = get_team_and_members(id)

    if request.user.is_authenticated:
        user = request.user

    users = User.objects.filter(is_superuser=False, teammembership__team=team).distinct()
   
    
    if request.method == 'POST':
        forms = [EditUserPermission(team, user, request.POST, prefix=str(user.id)) for user in users]
        for form in forms:
            if form.is_valid():
                user_id = form.prefix
                user = get_object_or_404(User, pk=user_id)
                group = form.cleaned_data.get('groups')

                team_membership = TeamMembership.objects.filter(user=user, team=team).first()
                if team_membership:
                    team_membership.groups.set([group]) if group else team_membership.groups.clear()
                    team_membership.save()
                    messages.success(request, f'Grupa użytkownika {user.get_full_name()} została pomyślnie zmieniona!')
   

                return redirect('team_permission', id=team.id)
    else:
        forms = [EditUserPermission(team, user, prefix=str(user.id)) for user in users]
            

    context = {'team':team, 'forms':forms, 'members': members, 'user':user}

    if check_perms(user, team,'manage_perms'):
        return render(request, 'teams/team_permission.html', context=context)
    else:
        raise Http404("Nie masz dostępu do tej strony!!!") 

@login_required
def team_add_member(request, id):
    team, members = get_team_and_members(id)

    if request.user.is_authenticated:
        user = request.user

    if request.method == 'POST':
        form = AddNewMember(request.POST or None, team=team)
        if form.is_valid():
            member = form.cleaned_data['members']
            group = form.cleaned_data['groups']
            
            team_membership = TeamMembership.objects.create(user = member, team=team)
            team_membership.groups.add(group)            
            return redirect('team_members', id=team.id)
    else:
        form = AddNewMember(team=team)
        form.team = team 

    context = {'team':team, 'form':form, 'members': members, 'user':user}

    if( check_perms(user, team, 'add_new_member') and check_perms(user, team, 'delete_member')):
        return render(request, 'teams/team_members.html', context=context)
    else:
        raise Http404("Nie masz dostępu do tej strony!!!")


@login_required
def remove_member(request, team_id, member_id):
    team = get_object_or_404(Team, id = team_id)
    member = get_object_or_404(User, id=member_id)

    team.members.remove(member)

    return redirect('team_members', id=team.id)
