import os
import secrets

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import DomainNameValidator, URLValidator, validate_slug
from django.db import models, transaction
from django.db.models import Q
from slugify import slugify

from hexa.core.models.base import Base, BaseManager, BaseQuerySet
from hexa.core.models.soft_delete import (
    DefaultSoftDeletedManager,
    IncludeSoftDeletedManager,
    SoftDeletedModel,
    SoftDeleteQuerySet,
)
from hexa.git.enums import FileEncoding
from hexa.git.mixins import GitOrg, GitRepoMixin
from hexa.shortcuts.mixins import ShortcutableMixin
from hexa.superset.models import SupersetDashboard
from hexa.user_management.models import ServicePrincipal, User, UserInterface
from hexa.webapps.validators import validate_subdomain
from hexa.workspaces.models import Workspace


def create_webapp_slug(name: str, workspace: Workspace):
    """Generate a unique slug for a webapp within a workspace."""
    suffix = ""
    while True:
        slug = slugify(name[: 100 - len(suffix)] + suffix)
        if not Webapp.all_objects.filter(workspace=workspace, slug=slug).exists():
            return slug
        suffix = "-" + secrets.token_hex(3)


def create_webapp_subdomain(slug: str, workspace: Workspace, max_tries=10):
    def is_valid_and_available(candidate):
        try:
            validate_subdomain(candidate)
        except ValidationError:
            return False
        return not Webapp.all_objects.filter(subdomain=candidate).exists()

    candidates = [slug, f"{workspace.slug}-{slug}"]
    for candidate in candidates:
        if is_valid_and_available(candidate):
            return candidate
    for _ in range(max_tries):
        candidate = f"{workspace.slug}-{slug}-{secrets.token_hex(3)}"
        if is_valid_and_available(candidate):
            return candidate
    raise ValueError(
        f"Could not generate a unique subdomain after {max_tries} attempts"
    )


class WebappQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: AnonymousUser | UserInterface):
        return self.filter(workspace__in=Workspace.objects.filter_for_user(user))

    def filter_favorites(self, user: User):
        return self.filter(favorites=user)


class WebappManager(
    BaseManager, DefaultSoftDeletedManager.from_queryset(WebappQuerySet)
):
    def create_if_has_perm(self, principal, ws, **kwargs):
        if not principal.has_perm("webapps.create_webapp", ws):
            raise PermissionDenied

        if kwargs.get("url"):
            URLValidator()(kwargs["url"])

        if "slug" not in kwargs:
            kwargs["slug"] = create_webapp_slug(kwargs["name"], ws)

        if "subdomain" in kwargs:
            validate_subdomain(kwargs["subdomain"])
        else:
            kwargs["subdomain"] = create_webapp_subdomain(kwargs["slug"], ws)

        kwargs["workspace"] = ws
        return super(BaseManager, self).create(**kwargs)


class AllWebappManager(
    BaseManager, IncludeSoftDeletedManager.from_queryset(WebappQuerySet)
):
    pass


class Webapp(Base, SoftDeletedModel, ShortcutableMixin):
    class Meta:
        verbose_name = "Webapp"
        constraints = [
            models.UniqueConstraint(
                "workspace_id",
                "name",
                name="unique_webapp_name_per_workspace",
                condition=Q(deleted_at__isnull=True),
            ),
            models.UniqueConstraint(
                "workspace_id",
                "slug",
                name="unique_webapp_slug_per_workspace",
                condition=Q(deleted_at__isnull=True),
            ),
        ]

    class WebappType(models.TextChoices):
        IFRAME = "iframe", "iFrame"
        STATIC = "static", "Static"
        SUPERSET = "superset", "Superset"

    class OperationScope(models.TextChoices):
        PIPELINES_RUN = "PIPELINES_RUN", "Run pipelines"
        PIPELINES_READ = "PIPELINES_READ", "Read pipelines"
        FILES_READ = "FILES_READ", "Read files"
        FILES_WRITE = "FILES_WRITE", "Write files"
        DATASETS_READ = "DATASETS_READ", "Read datasets"
        DATASETS_WRITE = "DATASETS_WRITE", "Write datasets"
        USER_READ = "USER_READ", "Read user info"

    name = models.CharField(max_length=255)
    slug = models.CharField(
        max_length=100, null=False, editable=False, validators=[validate_slug]
    )
    description = models.TextField(blank=True)
    icon = models.BinaryField(blank=True, null=True)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="webapps"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    # The external url for IFrame embedding, or the internal url for Superset Dashboards
    url = models.URLField(blank=True, default="")
    type = models.CharField(
        max_length=20, choices=WebappType.choices, default=WebappType.IFRAME
    )
    is_public = models.BooleanField(default=False)
    show_powered_by = models.BooleanField(default=True)
    subdomain = models.CharField(
        max_length=63,
        unique=True,
        validators=[validate_subdomain],
    )
    custom_domain = models.CharField(
        max_length=253,
        blank=True,
        null=True,
        unique=True,
        validators=[DomainNameValidator()],
    )
    favorites = models.ManyToManyField(
        User, related_name="favorite_webapps", blank=True
    )
    allowed_operations = models.JSONField(default=list, blank=True)
    objects = WebappManager()
    all_objects = AllWebappManager()

    @property
    def serve_url(self):
        if self.type == self.WebappType.IFRAME:
            return f"{settings.NEW_FRONTEND_DOMAIN}/workspaces/{self.workspace.slug}/webapps/{self.slug}/play"
        return f"{settings.SCHEME}://{self.subdomain}.{settings.WEBAPPS_DOMAIN}/"

    def is_favorite(self, user: User):
        return self.favorites.filter(pk=user.pk).exists()

    def add_to_favorites(self, user: User):
        self.favorites.add(user)
        self.save()

    def remove_from_favorites(self, user: User):
        self.favorites.remove(user)
        self.save()

    def delete_if_has_perm(self, principal):
        if not principal.has_perm("webapps.delete_webapp", self):
            raise PermissionDenied
        if self.type == Webapp.WebappType.SUPERSET:
            with transaction.atomic():
                dashboard = SupersetDashboard.objects.get(webapp__pk=self.pk)
                self.delete()
                dashboard.delete()
        elif self.type == Webapp.WebappType.STATIC:
            GitWebapp.objects.get(pk=self.pk).delete_if_has_perm(principal)
        else:
            self.delete()

    def to_shortcut_item(self):
        """Convert this webapp to a shortcut item dict for GraphQL"""
        return {"label": self.name, "url": self.serve_url}

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return f"<Webapp: {self.name}>"


class GitWebapp(Webapp, GitRepoMixin):
    published_commit = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["published_commit"], name="idx_gitwebapp_published_commit"
            ),
        ]

    @property
    def git_org(self):
        if self.workspace.organization:
            return GitOrg(
                slug=self.workspace.organization.slug,
                display_name=self.workspace.organization.name,
            )
        return GitOrg(slug="no-org", display_name="No Organization")

    def get_versions(self, page=1, per_page=20):
        items = self.client.get_commits(
            self.git_org.slug, self.repository, page=page, limit=per_page
        )
        return {"items": items, "page": page}

    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".xml": "xml",
        ".svg": "xml",
        ".sh": "shell",
        ".r": "r",
        ".sql": "sql",
    }

    def get_files(self, ref="main"):
        raw_files = self.client.get_repository_files(
            self.repository, ref, org_slug=self.git_org.slug
        )
        nodes = []
        for entry in raw_files:
            path = entry["path"]
            content = entry.get("content")
            encoding = entry.get("encoding")
            parent = "/".join(path.split("/")[:-1]) or None
            extension = os.path.splitext(path)[1].lower()
            is_text = encoding == FileEncoding.TEXT and content is not None

            nodes.append(
                {
                    "id": path,
                    "name": path.split("/")[-1],
                    "path": path,
                    "type": entry["type"],
                    "content": content,
                    "encoding": encoding,
                    "parent_id": parent,
                    "auto_select": path == "index.html",
                    "language": self.LANGUAGE_MAP.get(extension) if is_text else None,
                    "line_count": content.count("\n") + 1 if is_text else None,
                }
            )
        return nodes

    def get_commit_diff(self, sha: str) -> dict:
        raw = self.client.get_commit(self.git_org.slug, self.repository, sha)
        git_commit = raw.get("commit") or {}
        git_author = git_commit.get("author") or {}
        raw_diff = self.client.get_commit_diff(self.git_org.slug, self.repository, sha)
        return {
            "id": raw.get("sha", sha),
            "message": (git_commit.get("message") or "").strip(),
            "author_name": git_author.get("name", ""),
            "author_email": git_author.get("email", ""),
            "date": git_author.get("date", ""),
            "raw_diff": raw_diff,
        }

    def publish_version(self, version_id):
        if not self.client.commit_exists(
            self.git_org.slug, self.repository, version_id
        ):
            raise ValueError(f"Version {version_id} not found")
        self.published_commit = version_id
        self.save()

    def save_files(self, files, message, user):
        sha = self.client.commit_files(
            self.repository,
            files,
            message,
            user.display_name or user.email,
            user.email,
            org_slug=self.git_org.slug,
        )
        self.published_commit = sha
        self.save()
        return sha

    def delete_if_has_perm(self, principal):
        if not principal.has_perm("webapps.delete_webapp", self):
            raise PermissionDenied
        with transaction.atomic():
            self.delete()
            self.archive_repo()

    @classmethod
    def create_if_has_perm(
        cls,
        principal,
        workspace,
        *,
        name,
        created_by,
        webapp_type,
        description="",
        icon=None,
        is_public=False,
        files=None,
        allowed_operations=None,
    ):
        with transaction.atomic():
            webapp = cls.objects.create_if_has_perm(
                principal,
                workspace,
                type=webapp_type,
                name=name,
                description=description,
                icon=icon,
                is_public=is_public,
                created_by=created_by,
                allowed_operations=allowed_operations or [],
            )
            webapp.repository = f"{workspace.slug}-webapp-{webapp.slug}"

            initial_sha = webapp.create_repo(files=files, user=principal)
            webapp.published_commit = initial_sha
            webapp.save()

        return webapp


class SupersetWebapp(Webapp):
    superset_dashboard = models.OneToOneField(
        SupersetDashboard,
        on_delete=models.CASCADE,
        related_name="webapp",
    )

    @classmethod
    def create_if_has_perm(
        cls,
        principal,
        workspace,
        superset_instance,
        external_dashboard_id,
        *,
        name,
        created_by,
        description="",
        icon=None,
        is_public=False,
        allowed_operations=None,
    ):
        with transaction.atomic():
            dashboard = SupersetDashboard.objects.create(
                external_id=external_dashboard_id,
                superset_instance=superset_instance,
                name=name,
                description=description,
            )

            return cls.objects.create_if_has_perm(
                principal,
                workspace,
                superset_dashboard=dashboard,
                url=dashboard.get_absolute_url(),
                type=Webapp.WebappType.SUPERSET,
                name=name,
                description=description,
                icon=icon,
                is_public=is_public,
                created_by=created_by,
                allowed_operations=allowed_operations or [],
            )

    def update_dashboard(self, superset_instance, external_dashboard_id):
        self.superset_dashboard.external_id = external_dashboard_id
        self.superset_dashboard.superset_instance = superset_instance
        self.superset_dashboard.save()
        self.url = self.superset_dashboard.get_absolute_url()
        self.save()


class WebappUser(User, ServicePrincipal):
    class Meta:
        proxy = True

    webapp = None

    @classmethod
    def from_user(cls, user: User, webapp: Webapp) -> "WebappUser":
        """Cast an existing User row to a WebappUser view tied to `webapp`."""
        instance = cls.objects.get(pk=user.pk)
        instance.webapp = webapp
        return instance

    def get_username(self):
        return f"webapp_{self.webapp.id}_as_{self.email}"
