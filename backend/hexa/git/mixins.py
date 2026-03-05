from collections import namedtuple

from django.db import models

from hexa.git.client import GitClient
from hexa.git.forgejo import get_forgejo_client

GitOrg = namedtuple("GitOrg", ["slug", "display_name"])


class GitRepoMixin(models.Model):
    repository = models.CharField(max_length=255)

    class Meta:
        abstract = True

    @property
    def org(self) -> GitOrg:
        raise NotImplementedError("Child classes must implement the org property")

    @property
    def client(self) -> GitClient:
        return get_forgejo_client()

    def create_repo(self):
        self.client.create_organization(self.org.slug, self.org.display_name)
        self.client.create_org_repository(self.org.slug, self.repository)

    def delete_repo(self):
        self.client.delete_repository(self.org.slug, self.repository)

    def archive_repo(self):
        self.client.archive_repository(self.org.slug, self.repository)
