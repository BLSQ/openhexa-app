import uuid

from django.db import models
from django_countries.fields import CountryField


class PipelineServer(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hexa_owner = models.ForeignKey(
        "user_management.Organization", null=True, blank=True, on_delete=models.SET_NULL
    )
    hexa_name = models.CharField(max_length=200, blank=True)
    hexa_short_name = models.CharField(max_length=100, blank=True)
    hexa_description = models.TextField(blank=True)
    hexa_countries = CountryField(multiple=True, blank=True)
    hexa_last_synced_at = models.DateTimeField(null=True, blank=True)
    hexa_active_from = models.DateTimeField(null=True, blank=True)
    hexa_active_to = models.DateTimeField(null=True, blank=True)
    hexa_created_at = models.DateTimeField(auto_now_add=True)
    hexa_updated_at = models.DateTimeField(auto_now=True)
