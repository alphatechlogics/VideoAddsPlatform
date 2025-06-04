from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.home, name='home'),
    path('my-links/', views.my_links, name='my_links'),
    path('delete-link/<int:link_id>/', views.delete_link, name='delete_link'),
    path('all_data/', views.all_data, name='all_data'),
    path('update_last_checked/', views.update_last_checked, name='update_last_checked'),
        
    # Search endpoint with session auth
    path('search/', login_required(views.search_videos), name='search'),
]