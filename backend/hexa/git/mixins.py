import logging
from collections import namedtuple

from django.conf import settings
from django.db import models

from hexa.git.client import GitClient
from hexa.git.forgejo import ForgejoAPIError, get_forgejo_client
from hexa.user_management.models import User

logger = logging.getLogger(__name__)

GitOrg = namedtuple("GitOrg", ["slug", "display_name"])


class GitRepoMixin(models.Model):
    """A model whose history lives in a git repository of its own.

    What is declared here is what this class calls itself — `git_org`, and `has_history`
    for reading — following the template-method shape: a subclass answers those and
    inherits the reading side. Writing is deliberately *not* declared: committing means
    something different for each artifact (one file or a tree, a publishing pointer or a
    drift marker), and a signature covering both would fit neither. See `hexa/git`.
    """

    repository = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True

    @property
    def git_org(self) -> GitOrg:
        raise NotImplementedError("Child classes must implement the org property")

    @property
    def client(self) -> GitClient:
        return get_forgejo_client()

    @property
    def has_history(self) -> bool:
        """Whether the repository exists on the server and holds something to read.

        True by default, for the models that create the repository as they are created.
        A model that names a repository before creating one (as a migration introducing
        versioning leaves it) says so by overriding this.
        """
        return True

    def get_versions(self, page: int = 1, per_page: int = 20) -> dict:
        if not self.has_history:
            return {"items": [], "page": page}
        return {
            "items": self.client.get_commits(
                self.git_org.slug, self.repository, page=page, limit=per_page
            ),
            "page": page,
        }

    def get_commit_diff(self, sha: str) -> dict:
        return {
            **self.client.get_commit(self.git_org.slug, self.repository, sha),
            "raw_diff": self.client.get_commit_diff(
                self.git_org.slug, self.repository, sha
            ),
        }

    def create_repo(self, *, files: list[dict] | None = None, user: User) -> str:
        try:
            self.client.create_org_repository(
                self.git_org.slug, self.repository, auto_init=not files
            )
            self.client.protect_branch(self.git_org.slug, self.repository)
            if settings.GIT_PROXY_USERNAME:
                self.client.add_collaborator(
                    self.git_org.slug, self.repository, settings.GIT_PROXY_USERNAME
                )
        except ForgejoAPIError as e:
            if e.status_code == 409:
                logger.warning(
                    "Repository %s/%s already exists, reusing it",
                    self.git_org.slug,
                    self.repository,
                )
            else:
                raise

        if files:
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


class WorkspaceGitRepoMixin(GitRepoMixin):
    """A git-backed artifact belonging to a workspace.

    Every such artifact keeps its repository in the git organization of the workspace's
    organization, so the one thing `GitRepoMixin` asks of a subclass has a single
    answer worth writing once.
    """

    class Meta:
        abstract = True

    @property
    def git_org(self) -> GitOrg:
        return GitOrg(
            slug=self.workspace.organization.slug,
            display_name=self.workspace.organization.name,
        )
