import uuid
from django.db import models
from django_countries.fields import CountryField


class Base(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Content(Base):
    class Meta:
        abstract = True

    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    countries = CountryField(multiple=True, blank=True)

    @property
    def display_name(self):
        return self.short_name if self.short_name != "" else self.name

    def __str__(self):
        return self.display_name
