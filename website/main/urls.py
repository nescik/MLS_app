from django.urls import path
from . import views
from .views import PasswordsChangeView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('error', views.error_page, name='error_page'),
    path('sign-up', views.sign_up, name='sign-up'),
    path('my-login', views.my_login, name='my-login'),
    path('user-logout', views.user_logout, name="user-logout"),

    #User profile
    path('account-general', views.account_general, name='account-general'),
    path('account-change-password', PasswordsChangeView.as_view(template_name='user_profile/account_change_password.html'), name='account-change-password'),
    path('account-info', views.account_info, name='account-info'),
    path('account-social', views.account_social, name='account-social'),

    #Teams
    path('team/<int:id>/board', views.team_board, name='team_board'),
    path('team/<int:id>/files', views.team_files, name='team_files'),
    path('team/<int:id>/manage', views.team_manage, name='team_manage'),
    path('team/<int:id>/add_file', views.team_add_file, name='team_add_file'),
    path('team/<int:team_id>/edit_file/<int:file_id>', views.edit_file, name='edit_file'),
    path('team/<int:id>/permission', views.team_permission, name='team_permission'),
    path('team/<int:id>/members', views.team_add_member, name='team_members'),
    path('team/<int:id>/logs', views.team_logs, name='team_logs'),
    path('download/<int:id>', views.download_file, name='download_file'),
    path('team/<int:team_id>/remove_member/<int:member_id>', views.remove_member, name='remove_member'),
    path('team/<int:team_id>/remove_message/<int:message_id>', views.remove_message, name='remove_message'),
    path('team/<int:id>/delete', views.delete_team, name='delete_team')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)