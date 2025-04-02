from django.conf import settings
from django.db import models
from django.urls import reverse

from hexa.core.models.base import Base
from hexa.core.models.cryptography import EncryptedTextField
from hexa.superset.api import SupersetClient


class SupersetInstance(Base):
    name = models.CharField(max_length=255)
    url = models.URLField()

    # Make sure to not use a admin user as they do not have the same permissions (you won't be able to get the dashboards' list)
    api_username = models.CharField(max_length=255)
    api_password = EncryptedTextField()

    def get_client(self):
        return SupersetClient(self.url, self.api_username, self.api_password)


class SupersetDashboard(Base):
    external_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    superset_instance = models.ForeignKey(SupersetInstance, on_delete=models.CASCADE)

    def get_absolute_url(self):
        """Returns the URL to access this dashboard."""
        return f"{settings.NEW_FRONTEND_DOMAIN}{reverse('superset:dashboard', kwargs={'dashboard_id': self.id})}"

    class Meta:
        unique_together = ("external_id", "superset_instance")
        indexes = [
            models.Index(fields=["external_id"]),
        ]
