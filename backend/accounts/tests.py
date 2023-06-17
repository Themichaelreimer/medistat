from django.test import TestCase, SimpleTestCase, Client
import accounts.views as views
from accounts.models import Account

# Create your tests here.


class TestAuthViews(TestCase):
    USER_EMAIL = "test@test.com"
    USER_PASS = "testtesttest"

    def setUp(self) -> None:
        self.existing_user = Account.objects.create_user(self.USER_EMAIL, self.USER_EMAIL, self.USER_PASS)
        return super().setUp()

    def test_registration(self) -> None:
        client = Client()

        response_should_fail_duplicate_email = client.post(
            "/accounts/register/", data={"email": self.USER_EMAIL, "password1": "test1", "password2": "test1"}
        )
        self.assertEquals(400, response_should_fail_duplicate_email.status_code, response_should_fail_duplicate_email.content)
        self.assertEquals(
            "Could not register user: This email address already belongs to a user.", response_should_fail_duplicate_email.json().get("status")
        )

        response_should_fail_password_mismatch = client.post(
            "/accounts/register/", data={"email": "someguy@web.com", "password1": "test1", "password2": "test2"}
        )
        self.assertEquals(400, response_should_fail_password_mismatch.status_code, response_should_fail_password_mismatch.content)
        self.assertEquals("Could not register user: Passwords don't match.", response_should_fail_password_mismatch.json().get("status"))

        response_should_fail_bad_email = client.post(
            "/accounts/register/", data={"email": "someguy", "password1": "test1", "password2": "test1"}
        )
        self.assertEquals(400, response_should_fail_bad_email.status_code, response_should_fail_bad_email.content)
        self.assertEquals(
            f"Could not register user: `someguy` is not a valid email address.", response_should_fail_bad_email.json().get("status")
        )

        response_should_succeed = client.post(
            "/accounts/register/", data={"email": "someguy@web.com", "password1": "test1", "password2": "test1"}
        )
        self.assertEquals(200, response_should_succeed.status_code, response_should_succeed.content)
        self.assertEquals(f"Registration successful! Welcome to Medistat!", response_should_succeed.json().get("status"))

    def test_login(self) -> None:
        client = Client()

        resp = client.post("/accounts/login/", data={"email": self.USER_EMAIL, "password": self.USER_PASS})
        self.assertEquals(200, resp.status_code, resp.content)

        # Checks the correctness of the user data stored in session variables
        self.assertEquals(self.USER_EMAIL, client.session.get("user", {}).get("email"))
        self.assertEquals(str(client.session.get("user", {}).get("id")), client.session.get("_auth_user_id"))

    def test_logout(self) -> None:
        client = Client()
        client.login(username=self.USER_EMAIL, password=self.USER_PASS)

        # Convenience function to make test assertions more readable here
        is_logged_in = lambda x: bool(x.session.get("_auth_user_id"))

        self.assertTrue(is_logged_in(client), "Client should be logged in but isn't")

        # Logging out while logged in should succeed
        resp = client.post("/accounts/logout/")
        self.assertEquals(200, resp.status_code, resp.content)
        self.assertFalse(is_logged_in(client), "Client should be logged out but isn't")

        # Trying to log out again while logged out should generate a 401 Unauthenticated response
        resp = client.post("/accounts/logout/")
        self.assertEquals(401, resp.status_code, resp.content)
        self.assertFalse(is_logged_in(client), "Client should be logged out but isn't")
