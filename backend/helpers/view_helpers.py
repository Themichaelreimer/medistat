from django.http import JsonResponse, HttpRequest
from typing import Callable


def authenticated_endpoint(fcn: Callable) -> Callable:
    def inner(request: HttpRequest) -> JsonResponse:
        if request.user.is_authenticated:
            return fcn(request)
        else:
            return JsonResponse(status=401, data={"status": "You must be logged in to perform this action."})

    return inner


def generic_view_error_handler(fcn: Callable) -> Callable:
    def inner(*args, **argv) -> JsonResponse:  # type:ignore
        try:
            return fcn(*args, **argv)
        except Exception as e:
            # Expectation is, endpoints should handle their own errors, but this is a measure to reduce severity
            return JsonResponse(status=500, data={"status": "An unexpected error has occured. Please try again later."})

    return inner
