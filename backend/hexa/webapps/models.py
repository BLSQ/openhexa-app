import os
import secrets

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.validators import URLValidator, validate_slug
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
from hexa.git.mixins import GitOrg, GitRepoMixin
from hexa.shortcuts.mixins import ShortcutableMixin
from hexa.superset.models import SupersetDashboard
from hexa.user_management.models import User
from hexa.workspaces.models import Workspace


def create_webapp_slug(name: str, workspace: Workspace):
    """Generate a unique slug for a webapp within a workspace."""
    suffix = ""
    while True:
        slug = slugify(name[: 100 - len(suffix)] + suffix)
        if not Webapp.all_objects.filter(workspace=workspace, slug=slug).exists():
            return slug
        suffix = "-" + secrets.token_hex(3)


class WebappQuerySet(BaseQuerySet, SoftDeleteQuerySet):
    def filter_for_user(self, user: AnonymousUser | User):
        # FIXME: Use a generic permission system instead of differencing between User and PipelineRunUser
        from hexa.pipelines.authentication import PipelineRunUser

        if isinstance(user, PipelineRunUser):
            return self._filter_for_user_and_query_object(
                user,
                models.Q(workspace=user.pipeline_run.pipeline.workspace),
            )
        return self._filter_for_user_and_query_object(
            user,
            Q(workspace__members=user),
            return_all_if_superuser=True,
            return_all_if_organization_admin_or_owner=True,
        )

    def filter_favorites(self, user: User):
        return self.filter(favorites=user)


class WebappManager(
    BaseManager, DefaultSoftDeletedManager.from_queryset(WebappQuerySet)
):
    def create_if_has_perm(self, principal, ws, **kwargs):
        if not principal.has_perm(
            f"{self.model._meta.app_label}.create_{self.model._meta.model_name}", ws
        ):
            raise PermissionDenied

        if kwargs.get("url"):
            URLValidator()(kwargs["url"])

        if "slug" not in kwargs:
            kwargs["slug"] = create_webapp_slug(kwargs["name"], ws)

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
    url = models.URLField(blank=True, default="")
    type = models.CharField(
        max_length=20, choices=WebappType.choices, default=WebappType.IFRAME
    )
    is_public = models.BooleanField(default=False)
    favorites = models.ManyToManyField(
        User, related_name="favorite_webapps", blank=True
    )
    objects = WebappManager()
    all_objects = AllWebappManager()

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
            dashboard = SupersetDashboard.objects.get(webapp__pk=self.pk)
            self.delete()
            dashboard.delete()
        elif self.type == Webapp.WebappType.STATIC:
            GitWebapp.objects.get(pk=self.pk).delete_if_has_perm(principal)
        else:
            self.delete()

    def to_shortcut_item(self):
        """Convert this webapp to a shortcut item dict for GraphQL"""
        return {
            "label": self.name,
            "url": f"/workspaces/{self.workspace.slug}/webapps/{self.slug}/play",
        }

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
            parent = "/".join(path.split("/")[:-1]) or None
            extension = os.path.splitext(path)[1].lower()

            nodes.append(
                {
                    "id": path,
                    "name": path.split("/")[-1],
                    "path": path,
                    "type": entry["type"],
                    "content": content,
                    "parent_id": parent,
                    "auto_select": path == "index.html",
                    "language": self.LANGUAGE_MAP.get(extension) if content else None,
                    "line_count": content.count("\n") + 1 if content else None,
                }
            )
        return nodes

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
        self.archive_repo()
        self.delete()

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
    ):
        if not principal.has_perm("webapps.create_webapp", workspace):
            raise PermissionDenied

        webapp_slug = create_webapp_slug(name, workspace)
        with transaction.atomic():
            webapp = cls.objects.create(
                workspace=workspace,
                type=webapp_type,
                slug=webapp_slug,
                name=name,
                description=description,
                icon=icon,
                is_public=is_public,
                created_by=created_by,
                repository=f"{workspace.slug}-webapp-{webapp_slug}",
            )

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
    ):
        if not principal.has_perm("webapps.create_webapp", workspace):
            raise PermissionDenied

        with transaction.atomic():
            dashboard = SupersetDashboard.objects.create(
                external_id=external_dashboard_id,
                superset_instance=superset_instance,
                name=name,
                description=description,
            )

            return cls.objects.create(
                superset_dashboard=dashboard,
                workspace=workspace,
                url=dashboard.get_absolute_url(),
                type=Webapp.WebappType.SUPERSET,
                slug=create_webapp_slug(name, workspace),
                name=name,
                description=description,
                icon=icon,
                is_public=is_public,
                created_by=created_by,
            )

    def update_dashboard(self, superset_instance, external_dashboard_id):
        self.superset_dashboard.external_id = external_dashboard_id
        self.superset_dashboard.superset_instance = superset_instance
        self.superset_dashboard.save()
        self.url = self.superset_dashboard.get_absolute_url()
        self.save()
