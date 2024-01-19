from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign-up'),
    path('my-login', views.my_login, name='my-login'),
    path('user-logout', views.user_logout, name="user-logout"),

    #User profile
    path('account-general', views.account_general, name='account-general'),
    path('account-change-password', views.account_change_password, name='account-change-password'),
    path('account-info', views.account_info, name='account-info'),
    path('account-social', views.account_social, name='account-social')
]