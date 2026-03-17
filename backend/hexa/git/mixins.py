from collections import namedtuple

from django.db import models

from hexa.git.client import GitClient
from hexa.git.forgejo import get_forgejo_client

GitOrg = namedtuple("GitOrg", ["slug", "display_name"])


class GitRepoMixin(models.Model):
    repository = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True

    @property
    def git_org(self) -> GitOrg:
        raise NotImplementedError("Child classes must implement the org property")

    @property
    def client(self) -> GitClient:
        return get_forgejo_client()

    def create_repo(self, *, files=None, user=None) -> str:
        self.client.create_organization(self.git_org.slug, self.git_org.display_name)
        self.client.create_org_repository(
            self.git_org.slug, self.repository, auto_init=not (files and user)
        )
        if files and user:
            return self.client.commit_files(
                repo_name=self.repository,
                files=files,
                message="Initial content",
                author_name=user.display_name,
                author_email=user.email,
                org_slug=self.git_org.slug,
            )
        commits = self.client.get_commits(self.git_org.slug, self.repository, limit=1)
        return commits[0]["id"]

    def archive_repo(self):
        self.client.archive_repository(self.git_org.slug, self.repository)
