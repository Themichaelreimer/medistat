from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

from helpers.view_helpers import authenticated_endpoint

# Create your views here.


@csrf_exempt
def user_login(request: HttpRequest) -> JsonResponse:
    email = request.POST.get("email")
    password = request.POST.get("password")

    if user := authenticate(request, username=email, password=password):
        login(request, user)
        request.session["user"] = {"email": user.email, "id": user.id}  # type:ignore
        return JsonResponse(data={"status": "Authentication successful."})
    else:
        return JsonResponse(status=400, data={"status": "Authentication failed. Please try again."})


@authenticated_endpoint
def user_logout(request: HttpRequest) -> JsonResponse:
    logout(request)
    return JsonResponse(status=200, data={"status": "Logout successful."})
