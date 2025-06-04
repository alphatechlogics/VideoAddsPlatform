from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_views(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to your home page
        
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_views(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')  # Redirect to the login page