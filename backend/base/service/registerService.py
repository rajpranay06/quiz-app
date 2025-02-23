from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import login
from ..forms import CustomUserCreationForm
import json

# Define request body schema for registration
register_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the user', format='email'),
        'password1': openapi.Schema(type=openapi.TYPE_STRING, description='Password', format='password'),
        'password2': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm Password', format='password'),
    },
    required=['username', 'email', 'password1', 'password2']
)

# API - http://127.0.0.1:8000/register/  (POST request)
def registerPage(request):
    """
    User registration API.
    """
    form  = CustomUserCreationForm()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('lobby')
        else:
            messages.error(request, 'Registration failed')
            
    context = {"form": form}
    return render(request, 'base/login_register.html', context)