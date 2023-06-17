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

    def test_login(self) -> None:
        client = Client()

        resp = client.post("/accounts/login/", data={"email": self.USER_EMAIL, "password": self.USER_PASS})
        self.assertEquals(200, resp.status_code, resp.content)

        # Checks the correctness of the user data stored in session variables
        self.assertEquals(self.USER_EMAIL, client.session.get("user", {}).get("email"))
        self.assertEquals(client.session.get("user", {}).get("id"), client.session.get("_auth_user_id"))

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
