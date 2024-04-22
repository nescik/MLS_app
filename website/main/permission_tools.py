from django.contrib.auth.models import User
from django.http import Http404
from .models import TeamMembership

def check_perms(user, team, codename):
    team_membership = TeamMembership.objects.filter(user=user, team=team).first()

    if team_membership:
        if team_membership.groups.filter(permissions__codename=codename).exists():
            return True
        return False
    else:
        raise Http404("Nie należysz do tego zespołu!!!")


def get_user_perms(user, team):
    team_membership = TeamMembership.objects.filter(user=user, team=team).first()

    user_permissions = []
    if team_membership:
        group = team_membership.groups.first()

        if group:
            user_permissions += list(group.permissions.values_list('codename', flat=True))


    return user_permissions