from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import *




def home_page(request):
    return render(request, 'home.html')



def register(request):
    if request.method == "POST":
        data = request.POST
        if data:
            User.objects.create_user(
                username = data['username'],
                password = data['password'],
                photo = request.FILES['photo'],
                phone = data['phone'],
                about = data['about']
            )
    else: 
        return redirect('home')
    return render(request, 'registration.html')




def login_user(request):
    if request.method == "POST":
        data = request.POST
        user = authenticate(request, username = data['username'], password = data['password'])
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            return redirect('login')
    return render(request, 'login.html')



@login_required
def logout_user(request):
    logout(request)
    return redirect('login')




@login_required
def profile(request):
    return render(request, 'profile.html')




