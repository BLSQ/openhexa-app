from django import test
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from mock import patch

from hexa.plugins.connector_postgresql.models import (
    Database,
    DatasourceSyncResult,
)
from hexa.catalog.queue import datasource_sync_queue
from hexa.user_management.models import User


class AsyncRefreshTest(test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.SUPER_USER = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jim2021__",
            is_superuser=True,
        )
        cls.DATABASE_1 = Database.objects.create(
            hostname="localhost", username="db1", password="db1", database="db1"
        )

    @test.override_settings(DATASOURCE_ASYNC_REFRESH=False)
    def test_sync_refresh(self):
        self.client.force_login(self.SUPER_USER)
        synced = False

        def mock_sync(self):
            nonlocal synced
            synced = True
            return DatasourceSyncResult(
                datasource=self,
                created=10,
                updated=11,
                identical=12,
                orphaned=13,
            )

        with patch("hexa.plugins.connector_postgresql.models.Database.sync", mock_sync):
            url = reverse(
                "catalog:datasource_sync",
                args=[
                    ContentType.objects.get_for_model(Database).id,
                    self.DATABASE_1.id,
                ],
            )
            response = self.client.post(url, HTTP_REFERER="/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(synced)

    @test.override_settings(DATASOURCE_ASYNC_REFRESH=True)
    def test_async_refresh(self):
        self.client.force_login(self.SUPER_USER)
        synced = False

        def mock_sync(self):
            nonlocal synced
            synced = True
            return DatasourceSyncResult(
                datasource=self,
                created=10,
                updated=11,
                identical=12,
                orphaned=13,
            )

        with patch("hexa.plugins.connector_postgresql.models.Database.sync", mock_sync):
            url = reverse(
                "catalog:datasource_sync",
                args=[
                    ContentType.objects.get_for_model(Database).id,
                    self.DATABASE_1.id,
                ],
            )
            response = self.client.post(url, HTTP_REFERER="/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(synced)

        with patch("hexa.plugins.connector_postgresql.models.Database.sync", mock_sync):
            while datasource_sync_queue.run_once():
                pass

        self.assertTrue(synced)

    @test.override_settings(DATASOURCE_ASYNC_REFRESH=True)
    def test_sync_errors(self):
        self.client.force_login(self.SUPER_USER)
        url = reverse("catalog:datasource_sync", args=[55555, self.DATABASE_1.id])
        response = self.client.post(url, HTTP_REFERER="/", follow=True)
        assert response.status_code == 404

        url = reverse(
            "catalog:datasource_sync",
            args=[
                ContentType.objects.get_for_model(Database).id,
                "766c1165-2335-4108-885d-4b038839f264",
            ],
        )
        response = self.client.post(url, HTTP_REFERER="/", follow=True)
        assert response.status_code == 404
