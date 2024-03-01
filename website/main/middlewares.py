from django.shortcuts import redirect
from django.urls import resolve

class CheckPermissionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        required_permissions = getattr(view_func, 'required_permissions', [])

        user_permissions = request.user.get_all_permissions()
        if not all(perm in user_permissions for perm in required_permissions):
            return redirect('error_page')

        return None