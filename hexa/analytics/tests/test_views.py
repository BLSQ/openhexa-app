from django.urls import reverse

from hexa.core.test import TestCase
from hexa.user_management.models import User


class AnalyticsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER = User.objects.create_user(
            "user@bluesquarehub.com",
            "user_password",
        )

    def test_track_event_bad_request(self):
        self.client.force_login(self.USER)
        r = self.client.post(
            reverse(
                "analytics:track",
            ),
            {"properties": {}},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json(), {"Bad request": "event name is required."})

    def test_track_event(self):
        self.client.force_login(self.USER)
        r = self.client.post(
            reverse(
                "analytics:track",
            ),
            {"event": "page_viewed", "properties": {"page": "database"}},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 200)

    def test_track_event_analytics_not_enabled(self):
        self.USER.analytics_enabled = False
        self.USER.save()
        self.client.force_login(self.USER)
        r = self.client.post(
            reverse(
                "analytics:track",
            ),
            {"event": "page_viewed", "properties": {"page": "database"}},
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.json(), {"error": "Analytics not enabled."})
