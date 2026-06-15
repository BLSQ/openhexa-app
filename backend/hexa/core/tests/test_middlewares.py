from django.test import override_settings

from hexa.core.test import TestCase


@override_settings(DATA_UPLOAD_MAX_MEMORY_SIZE=10)
class RequestTooBigMiddlewareTest(TestCase):
    def test_oversized_post_returns_413_json_and_logs_to_security_logger(self):
        with self.assertLogs("django.security.RequestDataTooBig", level="ERROR") as cm:
            response = self.client.post(
                "/graphql/",
                data="x" * 1000,
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json(), {"error": "REQUEST_TOO_LARGE"})
        self.assertTrue(
            any("DATA_UPLOAD_MAX_MEMORY_SIZE" in line for line in cm.output),
            f"Expected security log to mention DATA_UPLOAD_MAX_MEMORY_SIZE, got {cm.output}",
        )
