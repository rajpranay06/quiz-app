from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages


# Define the request body schema for login
login_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user', format='password'),
    },
    required=['username', 'password']
)

# API - http://127.0.0.1:8000/login/ (POST request)
def loginPage(request):
    """
    User login API.
    """
    page = "login"
    
    if request.user.is_authenticated:
        return redirect('lobby')
    
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            pass
            #messages.error(request, 'User not found')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Hello {username}".format(username=username))
            return redirect('lobby')
        else:
            messages.error(request, 'Invalid credentials')
        
    context = {"page": page}
    return render(request, 'base/login_register.html', context)

