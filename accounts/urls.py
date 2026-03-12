from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),
]
