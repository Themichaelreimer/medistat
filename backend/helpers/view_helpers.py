from django.http import JsonResponse, HttpRequest
from typing import Callable


def authenticated_endpoint(fcn: Callable) -> Callable:
    def inner(request: HttpRequest) -> JsonResponse:
        try:
            if request.user.is_authenticated:
                return fcn(request)
            else:
                return JsonResponse(status=401, data={"status": "You must be logged in to perform this action."})

        except Exception as e:
            # General exception handler, should log info and return a general response
            # Expectation is, endpoints should handle their own errors, but this is a measure to reduce severity
            return JsonResponse(status=500, data={"status": "An unexpected error has occured. Please try again later."})

    return inner
