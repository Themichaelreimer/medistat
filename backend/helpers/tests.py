from django.test import SimpleTestCase
from django.http import JsonResponse, HttpRequest
from typing import Union

from helpers.view_helpers import authenticated_endpoint


# To make testing the wrapper easier, I make an object that matches the relevent parts of the request structure
# Advantages to this approach:
#   - Breaks the coupling with the implementation of the user object (since we dont have to make a user to test auth)
#   - Avoids complexity with calling test endpoints directly
#   - Enables us to use SimpleTestCase which is *way* more efficient because there is no database connection, rollback, etc
class FakeRequestObject:
    class __FakeUserObject:
        def __init__(self, is_authenticated: bool) -> None:
            self.is_authenticated = is_authenticated

    def __init__(self, is_authenticated: bool) -> None:
        self.user = FakeRequestObject.__FakeUserObject(is_authenticated)


@authenticated_endpoint
def fake_authenticated_endpoint(request: Union[FakeRequestObject, HttpRequest]) -> JsonResponse:
    return JsonResponse(status=200, data={"status": "ok"})


def fake_unauthenticated_endpoint(request: Union[FakeRequestObject, HttpRequest]) -> JsonResponse:
    return JsonResponse(status=200, data={"status": "ok"})


class TestViewHelpers(SimpleTestCase):
    def test_authenticated_endpoint(self) -> None:
        unauthenticated_request = FakeRequestObject(False)
        authenticated_request = FakeRequestObject(True)

        response_that_should_fail = fake_authenticated_endpoint(unauthenticated_request)
        response_that_should_succeed_1 = fake_authenticated_endpoint(authenticated_request)
        response_that_should_succeed_2 = fake_unauthenticated_endpoint(unauthenticated_request)
        # A little redundant, but I like that it clearly covers every combination of variables
        response_that_should_succeed_3 = fake_unauthenticated_endpoint(authenticated_request)

        self.assertEquals(401, response_that_should_fail.status_code)
        self.assertEquals(200, response_that_should_succeed_1.status_code)
        self.assertEquals(200, response_that_should_succeed_2.status_code)
        self.assertEquals(200, response_that_should_succeed_3.status_code)
