from collections import namedtuple

from django.db import models

from hexa.git.client import GitClient
from hexa.git.forgejo import ForgejoAPIError, get_forgejo_client
from hexa.user_management.models import User

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

    def create_repo(self, *, files: list[dict] | None = None, user: User) -> str:
        org_slug = self.git_org.slug
        repo_name = self.repository

        try:
            self.client.create_org_repository(org_slug, repo_name, auto_init=not files)
        except ForgejoAPIError as e:
            if e.status_code != 409:
                raise

        if files:
            return self.client.commit_files(
                repo_name=repo_name,
                files=files,
                message="Initial content",
                author_name=user.display_name,
                author_email=user.email,
                org_slug=org_slug,
            )
        commits = self.client.get_commits(org_slug, repo_name, limit=1)
        return commits[0]["id"]

    def archive_repo(self):
        self.client.archive_repository(self.git_org.slug, self.repository)
