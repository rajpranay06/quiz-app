from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt


# API - http://127.0.0.1:8000/logout/
@csrf_exempt
@api_view(['POST'])
def logoutUser(request):
    logout(request)
    return Response({"message": "Logout successful"}, status=200)