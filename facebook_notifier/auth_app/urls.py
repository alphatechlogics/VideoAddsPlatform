from django.urls import path
from . import views

app_name = 'auth_app'  # Add this line to namespace the app
urlpatterns = [
    path('login/', views.login_views, name='login'),
    path('logout/', views.logout_views, name='logout'),
]