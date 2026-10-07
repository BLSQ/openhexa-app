from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from hexa.core.middlewares import SSEAwareGZipMiddleware
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


@override_settings(STATIC_ROOT=settings.BASE_DIR / "hexa" / "static")
class SSEAwareGZipMiddlewareTest(TestCase):
    def test_conditional_static_request_is_not_compressed(self):
        first = self.client.get("/static/img/favicon.png", HTTP_ACCEPT_ENCODING="gzip")
        self.assertEqual(200, first.status_code)

        response = self.client.get(
            "/static/img/favicon.png",
            HTTP_ACCEPT_ENCODING="gzip",
            HTTP_IF_NONE_MATCH=first["ETag"],
        )

        self.assertEqual(304, response.status_code)
        self.assertNotIn("Content-Encoding", response)
        self.assertEqual(b"", b"".join(response.streaming_content))

    def test_html_response_is_gzipped(self):
        request = RequestFactory().get("/", HTTP_ACCEPT_ENCODING="gzip")
        response = SSEAwareGZipMiddleware(
            lambda r: HttpResponse("<html>" + "x" * 500)
        ).process_response(request, HttpResponse("<html>" + "x" * 500))

        self.assertEqual("gzip", response["Content-Encoding"])
