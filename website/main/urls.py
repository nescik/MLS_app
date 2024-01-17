from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign-up'),
    path('my-login', views.my_login, name='my-login'),
    path('user-logout', views.user_logout, name="user-logout"),
]