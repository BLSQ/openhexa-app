from django.db import models
from django_countries.fields import CountryField

from hexa.core.models import Base


class AccessmodQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        raise NotImplementedError(
            "Catalog querysets should implement the filter_for_user() method"
        )


class ProjectQuerySet(AccessmodQuerySet):
    def filter_for_user(self, user):
        return self.filter(owner=user)


class Project(Base):
    name = models.TextField()
    country = CountryField()
    owner = models.ForeignKey("user_management.User", on_delete=models.CASCADE)

    objects = ProjectQuerySet.as_manager()
