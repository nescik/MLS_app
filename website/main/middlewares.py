from django.shortcuts import redirect
from django.contrib.auth.models import Permission
from .models import TeamMembership, Team

class CheckPermissionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        required_permissions = getattr(view_func, 'required_permissions', [])

        # Sprawdź, czy użytkownik jest zalogowany
        if request.user.is_authenticated:
            # Pobierz identyfikator aktualnie przeglądanego zespołu (przyjmuję, że jest to przekazywane w parametrze widoku)
            team_id = view_kwargs.get('id')

            # Pobierz obiekt TeamMembership dla użytkownika i zespołu
            team_membership = TeamMembership.objects.filter(user=request.user, team_id=team_id).first()

            # Pobierz uprawnienia z TeamMembership, a następnie z grupy
            if team_membership:
                group = team_membership.groups.first()
                if group:
                    group_permissions = Permission.objects.filter(group=group)
                    user_permissions = [perm.codename for perm in group_permissions]

                    # Sprawdź, czy użytkownik ma odpowiednie uprawnienia
                    if all(perm in user_permissions for perm in required_permissions):
                        return None  # Jeśli ma uprawnienia, zakończ sprawdzanie
                    else:
                        return redirect('error_page')  # Przekieruj na stronę błędu, jeśli brak uprawnień
