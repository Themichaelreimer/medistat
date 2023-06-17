from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from helpers.view_helpers import authenticated_endpoint, generic_view_error_handler
from accounts.models import Account


@csrf_exempt
@generic_view_error_handler
def user_login(request: HttpRequest) -> JsonResponse:
    email = request.POST.get("email")
    password = request.POST.get("password")

    if user := authenticate(request, username=email, password=password):
        login(request, user)
        request.session["user"] = {"email": user.email, "id": user.id}  # type:ignore
        return JsonResponse(status=200, data={"status": "Authentication successful."})
    else:
        return JsonResponse(status=400, data={"status": "Authentication failed. Please try again."})


@csrf_exempt
@generic_view_error_handler
def user_register(request: HttpRequest) -> JsonResponse:
    """
    Registers a user via email and password.
    This is a placeholder that will be replaced with oauth later
    """
    email = request.POST.get("email")
    password1 = request.POST.get("password1")
    password2 = request.POST.get("password2")

    if Account.objects.filter(username=email).exists():
        return JsonResponse(status=400, data={"status": "Could not register user: This email address already belongs to a user."})
    if password1 != password2:
        return JsonResponse(status=400, data={"status": "Could not register user: Passwords don't match."})
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse(status=400, data={"status": f"Could not register user: `{email}` is not a valid email address."})

    account = Account.objects.create_user(email, email, password1)  # order of parameters is (username, email, password), and username is email
    login(request, account)

    return JsonResponse(status=200, data={"status": "Registration successful! Welcome to Medistat!"})


@authenticated_endpoint
@generic_view_error_handler
def user_logout(request: HttpRequest) -> JsonResponse:
    logout(request)
    return JsonResponse(status=200, data={"status": "Logout successful."})
