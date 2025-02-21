from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
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
@csrf_exempt
@swagger_auto_schema(method='post', request_body=register_schema, responses={201: "Registration successful", 400: "Registration failed"})
@api_view(['POST'])
def registerPage(request):
    """
    User registration API.
    """
    data = request.data
    form = CustomUserCreationForm(data)

    if form.is_valid():
        user = form.save(commit=False)
        user.username = user.username.lower()
        user.save()
        login(request, user)
        return Response({"message": "Registration successful", "user": user.username}, status=201)
    else:
        errors = form.errors.as_json()
        return Response({"error": "Registration failed", "details": errors}, status=400)