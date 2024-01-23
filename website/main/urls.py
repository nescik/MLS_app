from django.urls import path
from . import views
from .views import PasswordsChangeView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign-up'),
    path('my-login', views.my_login, name='my-login'),
    path('user-logout', views.user_logout, name="user-logout"),

    #User profile
    path('account-general', views.account_general, name='account-general'),
    path('account-change-password', PasswordsChangeView.as_view(template_name='user_profile/account_change_password.html'), name='account-change-password'),
    path('account-info', views.account_info, name='account-info'),
    path('account-social', views.account_social, name='account-social'),

    #Teams
    path('team/<int:id>', views.team_detail, name='team_detail')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)