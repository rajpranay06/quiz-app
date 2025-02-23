from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages


# API - http://127.0.0.1:8000/logout/
def logoutUser(request):
    logout(request)
    return redirect('home')