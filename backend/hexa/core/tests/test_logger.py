from unittest.mock import patch

from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import User


class LoggerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.SUPER_USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim2021__",
            is_superuser=True,
        )

    def test_logger(self):
        self.client.force_login(self.SUPER_USER)
        logs = []

        class mock_logger:
            def info(self, msg, *args, **kwargs):
                nonlocal logs
                logs.append(["INFO", msg])

            def warning(self, msg, *args, **kwargs):
                nonlocal logs
                logs.append(["WARNING", msg])

            def error(self, msg, *args, **kwargs):
                nonlocal logs
                logs.append(["ERROR", msg])

            def exception(self, msg, *args, **kwargs):
                nonlocal logs
                logs.append(["EXCEPTION", msg])

        with patch("hexa.core.views.logger", mock_logger()):
            url = reverse("core:test_logger")
            response = self.client.get(
                url, data={"level": "WARNING", "message": "test1"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[-1], ["WARNING", "test1"])

            self.client.get(url, data={"level": "INFO", "message": "test2"})
            self.assertEqual(logs[-1], ["INFO", "test2"])

            self.client.get(url, data={"message": "test3"})
            self.assertEqual(logs[-1], ["INFO", "test3"])

            self.client.get(url, data={"level": "ERROR", "message": "test4"})
            self.assertEqual(logs[-1], ["ERROR", "test4"])

            self.client.get(url, data={"level": "EXCEPTION", "message": "test5"})
            self.assertEqual(logs[-1], ["EXCEPTION", "test_logger"])

            with self.assertRaises(Exception):
                self.client.get(
                    url, data={"level": "UNCATCHED_EXCEPTION", "message": "test6"}
                )
