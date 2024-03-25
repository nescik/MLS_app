from .models import Team

def user_teams(request):
    if request.user.is_authenticated:
        user_teams = Team.objects.filter(members = request.user)
    else:
        user_teams = None
    return {'user_teams':user_teams}