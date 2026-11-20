from django.test import override_settings

from hexa.core.test import GraphQLTestCase
from hexa.user_management.models import User

LOGIN_MUTATION = """
    mutation login($input: LoginInput!) {
        login(input: $input) {
            success
            errors
        }
    }
"""
PASSWORD = "jimspassword"
LOCKED_OUT = {"success": False, "errors": ["TOO_MANY_ATTEMPTS"]}


@override_settings(PASSWORD_LOGIN_ENABLED=True, AXES_ENABLED=True)
class LoginRateLimitTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user("jim@bluesquarehub.com", PASSWORD)

    def login(self, password, forwarded_for="203.0.113.1"):
        return self.run_query(
            LOGIN_MUTATION,
            {"input": {"email": self.USER.email, "password": password}},
            headers={"HTTP_X_FORWARDED_FOR": forwarded_for},
        )["data"]["login"]

    def fail_logins(self, count, forwarded_for="203.0.113.1"):
        for _ in range(count):
            self.assertEqual(
                {"success": False, "errors": ["INVALID_CREDENTIALS"]},
                self.login("wrong", forwarded_for),
            )

    def test_locks_out_on_the_tenth_failure_even_with_the_right_password(self):
        self.fail_logins(9)

        self.assertEqual(LOCKED_OUT, self.login("wrong"))
        self.assertEqual(LOCKED_OUT, self.login(PASSWORD))

    def test_another_client_ip_is_also_locked_out(self):
        self.fail_logins(9, forwarded_for="203.0.113.1")
        self.assertEqual(LOCKED_OUT, self.login("wrong", forwarded_for="203.0.113.1"))

        self.assertEqual(LOCKED_OUT, self.login(PASSWORD, forwarded_for="203.0.113.2"))

    def test_a_successful_login_resets_the_count(self):
        self.fail_logins(9)
        self.assertEqual({"success": True, "errors": None}, self.login(PASSWORD))
        self.client.logout()

        self.fail_logins(9)
        self.assertEqual({"success": True, "errors": None}, self.login(PASSWORD))
