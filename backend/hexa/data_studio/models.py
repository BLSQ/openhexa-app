import secrets
from collections import defaultdict

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.validators import validate_slug
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from slugify import slugify

from hexa.core.models.base import Base, BaseQuerySet
from hexa.databases.query_text import sanitize_sql
from hexa.git.enums import FileEncoding
from hexa.git.mixins import GitOrg, GitRepoMixin
from hexa.user_management.models import ServicePrincipal, User, UserInterface
from hexa.workspaces.models import Workspace

SLUG_MAX_LENGTH = 255
SLUG_COLLISION_ATTEMPTS = 8

# The single file each saved query repository holds. Only the SQL is versioned:
# name, description and visibility are current-state attributes of the query, so a
# rename is not a new version of what the query *does*.
QUERY_FILE_PATH = "query.sql"


def generate_saved_query_slug(name: str) -> str:
    """Build a slug unique across all workspaces, suffixing on collision."""
    suffix = ""
    for _attempt in range(SLUG_COLLISION_ATTEMPTS):
        # A name made only of characters slugify drops (punctuation, emoji)
        # leaves nothing to build on, and an empty slug would make the query
        # unaddressable by the endpoints keyed on it.
        slug = slugify(name[: SLUG_MAX_LENGTH - len(suffix)] + suffix) or "query"
        if not SavedQuery.objects.filter(slug=slug).exists():
            return slug
        suffix = "-" + secrets.token_hex(3)

    raise RuntimeError(
        f"Could not generate a unique saved query slug for {name!r} "
        f"in {SLUG_COLLISION_ATTEMPTS} attempts"
    )


class SavedQueryVisibility(models.TextChoices):
    PRIVATE = "PRIVATE", _("Private")
    WORKSPACE = "WORKSPACE", _("Workspace")


class SavedQueryQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | UserInterface) -> models.QuerySet:
        accessible = models.Q(visibility=SavedQueryVisibility.WORKSPACE)
        # Service principals (pipeline runs, webapps) impersonate a workspace rather
        # than a person, so they never own a private query - a deliberate call for
        # WebappUser, whose real User row `created_by` would match and which
        # WorkspaceQuerySet does treat as a person.
        if isinstance(user, User) and not isinstance(user, ServicePrincipal):
            accessible |= models.Q(created_by=user)

        return self._filter_for_user_and_query_object(
            user,
            models.Q(workspace__in=Workspace.objects.filter_for_user(user))
            & accessible,
        )


class SavedQueryManager(models.Manager):
    def create_if_has_perm(
        self,
        principal: User,
        workspace: Workspace,
        *,
        name: str,
        content: str,
        description: str = "",
        # None means "unspecified" and lands on the default: a brand-new query is
        # private until its author decides to share it.
        visibility: str | None = None,
    ):
        if not principal.has_perm("data_studio.create_saved_query", workspace):
            raise PermissionDenied

        # The commit is inside the transaction on purpose: a saved query that exists
        # without the repository holding its first version has no history to browse and
        # no way to notice it is missing one, so a git failure takes the row with it.
        with transaction.atomic():
            saved_query = self.create(
                workspace=workspace,
                created_by=principal,
                name=name,
                content=content,
                description=description,
                visibility=visibility or SavedQueryVisibility.PRIVATE,
            )
            saved_query.record_version(principal)
            saved_query.save(update_fields=["repository", "last_commit"])

        return saved_query


# Every SavedQueryVisibility must appear here: a new visibility has to state whether
# its queries outlive their author, and there is no sane default to fall back on.
ON_AUTHOR_DELETED = {
    # Nothing but its author can reach a private query - no workspace or organization
    # role grants access to one - so leaving it behind would keep a row alive that
    # only a superuser could still see.
    #
    # CASCADE nulls the foreign key before deleting on backends that cannot defer
    # constraint checks, which the check constraint below would reject. PostgreSQL
    # defers, and it is the only backend OpenHEXA runs on - pinned by
    # `test_the_backend_can_defer_constraint_checks`. On a backend that cannot, drop
    # the delegation for a handler that collects without the field update:
    #
    #     collector.collect(sub_objs, source=field.remote_field.model,
    #                       source_attr=field.name, nullable=field.null,
    #                       fail_on_restricted=False)
    #
    # `source_attr` is what nests the queries under the user in the admin's delete
    # confirmation, so it is not optional.
    SavedQueryVisibility.PRIVATE: models.CASCADE,
    # Shared queries outlive their author: colleagues, and the webapps and pipelines
    # built on them, depend on queries they did not write.
    SavedQueryVisibility.WORKSPACE: models.SET_NULL,
}


def _policy_for(visibility: str):
    try:
        return ON_AUTHOR_DELETED[visibility]
    except KeyError:
        raise ImproperlyConfigured(
            f"No author-deletion policy for saved query visibility {visibility!r}:"
            " every visibility must state whether its queries outlive their author."
        ) from None


def saved_queries_on_author_deleted(collector, field, sub_objs, using):
    """`on_delete` for SavedQuery.created_by: what a query survives depends on who could read it.

    Nullifying every query would strand the private ones - rows no role can reach,
    kept forever for nobody - while deleting every query would break shared ones their
    workspace still relies on. The split mirrors the access rule in
    SavedQueryQuerySet.filter_for_user: what survives is exactly what someone other
    than the author could already read.

    What this is *not* is an erasure policy: it removes queries that became
    unreachable, not everything the account left behind. QueryLog keeps the text of
    what that user ran (see QueryLog.user).

    This is deliberately enforced at the model layer: user deletion happens through
    the Django admin or a shell, so any policy living in a service or a mutation
    would simply be bypassed.
    """
    by_policy = defaultdict(list)
    for saved_query in sub_objs:
        by_policy[_policy_for(saved_query.visibility)].append(saved_query)

    for policy, saved_queries in by_policy.items():
        policy(collector, field, saved_queries, using)


class SavedQuery(Base, GitRepoMixin):
    """A SQL query saved by a user in the Data Studio.

    A saved query belongs to a workspace, but its `visibility` decides who within
    that workspace can reach it: WORKSPACE queries are shared with every member,
    PRIVATE ones are the author's alone.

    Losing access and losing the author are two different things: a member removed
    from the workspace stops seeing their private queries but gets them back if they
    are added again, while deleting the account itself takes them for good (see
    `saved_queries_on_author_deleted`).

    Its history lives in a git repository of its own (one file, `query.sql`), the same
    way a static web app's does — see `hexa.git` for what that buys and what it costs.
    `content` here stays the source of truth: running a query, exporting it and listing
    it must not depend on the git server being reachable, so git is written through on
    save and only read when someone asks for history.
    """

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="saved_queries",
    )
    created_by = models.ForeignKey(
        User, null=True, on_delete=saved_queries_on_author_deleted
    )
    name = models.CharField(max_length=255, null=False, blank=False)
    # Stable public identifier: web apps address a saved query by slug, so it is
    # generated once and left alone when the query is renamed. Unique across all
    # workspaces, so the slug alone identifies a query and callers need not pair
    # it with a workspace.
    slug = models.CharField(
        max_length=SLUG_MAX_LENGTH, editable=False, validators=[validate_slug]
    )
    description = models.TextField(blank=True, default="")
    content = models.TextField()
    visibility = models.CharField(
        max_length=20,
        choices=SavedQueryVisibility.choices,
        default=SavedQueryVisibility.PRIVATE,
    )
    # The sha of the version holding `content`. Not a published pointer (there is no
    # publishing here — the current version is what runs): it says which commit the
    # column matches, so a drift between the two can be found rather than guessed at.
    # Null on a query whose repository was never created, which is what
    # `backfill_saved_query_repositories` looks for.
    last_commit = models.CharField(max_length=64, blank=True, null=True)

    objects = SavedQueryManager.from_queryset(SavedQueryQuerySet)()

    class Meta:
        verbose_name_plural = "saved queries"
        ordering = ["-updated_at"]
        constraints = [
            # An author-less private query is readable by nobody, so it can only be
            # dead weight. `saved_queries_on_author_deleted` is what keeps that from
            # happening; this makes any other code path that forgets an author fail
            # where it writes instead of leaving an invisible row behind.
            models.CheckConstraint(
                condition=models.Q(created_by__isnull=False)
                | ~models.Q(visibility=SavedQueryVisibility.PRIVATE),
                name="data_studio_private_query_has_author",
            ),
            models.UniqueConstraint(fields=["slug"], name="unique_saved_query_slug"),
        ]
        indexes = [
            # `id` mirrors the tiebreaker the listing resolver appends: without it
            # Postgres can only presort on the leading column and still has to run an
            # incremental sort on top of the index scan.
            models.Index(
                fields=["workspace", "-updated_at", "id"],
                name="data_studio_ws_updated_idx",
            ),
            models.Index(
                fields=["workspace", "name", "id"],
                name="data_studio_ws_name_idx",
            ),
            # Listings match `workspace = X AND (visibility = 'WORKSPACE' OR
            # created_by = me)`. Postgres serves that OR as a BitmapOr, so the two
            # indexes above cover the shared branch and this one covers the author
            # branch. `visibility` is deliberately not folded into their leading
            # columns: a BitmapOr discards index ordering anyway, so it would buy
            # nothing. If this ever shows up in profiling, the next step is partial
            # indexes, not a reshuffle here.
            models.Index(
                fields=["workspace", "created_by", "-updated_at", "id"],
                name="data_studio_ws_author_idx",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        # SQL pasted from a chat, a document or a PDF carries blanks PostgreSQL
        # rejects; cleaning them here means a query is stored runnable whichever
        # way it was written (editor, admin, ...).
        self.content = sanitize_sql(self.content)
        # Generated here rather than in the manager (as pipelines do) because the
        # Django admin creates saved queries through a plain form, which would
        # otherwise hit the not-null column with nothing in it.
        if not self.slug:
            self.slug = generate_saved_query_slug(self.name)
        # Same reason, and the column is unique too, so leaving it empty would let the
        # first admin-created query through and collide on the second. Naming the
        # repository costs nothing and reaches nothing; creating it is a separate step
        # (`record_version`), which is why a query can exist before its history does.
        if not self.repository:
            self.repository = self.default_repository_name()
        return super().save(*args, **kwargs)

    def default_repository_name(self) -> str:
        """The repository this query's history lives in.

        Named after the pk rather than the slug: a deleted query releases its slug, and
        reusing one would land on the archived repository that query left behind — which
        `create_repo` reports as "already exists, reusing it" before the commit fails on
        a repository that is read-only. The migration that introduced versioning derives
        the same name.
        """
        return f"{self.workspace.slug}-query-{self.id}"

    @property
    def git_org(self) -> GitOrg:
        return GitOrg(
            slug=self.workspace.organization.slug,
            display_name=self.workspace.organization.name,
        )

    def record_version(self, user: User, message: str = "Update query") -> str:
        """Commit the current content as a new version and return its sha.

        Creates the repository on the way when this query has none, which is what makes
        the write path self-healing for queries that predate versioning (the ones
        `backfill_saved_query_repositories` exists to catch).
        """
        file = {
            "path": QUERY_FILE_PATH,
            "content": self.content,
            "encoding": FileEncoding.TEXT,
        }
        # `last_commit`, not `repository`, is what says the repository exists on the
        # server: the migration that introduced versioning named the repository of every
        # query that already existed without creating a single one.
        if not self.last_commit:
            if not self.repository:
                self.repository = self.default_repository_name()
            sha = self.create_repo(files=[file], user=user)
        else:
            sha = self.client.commit_files(
                repo_name=self.repository,
                files=[file],
                message=message,
                author_name=user.display_name or user.email,
                author_email=user.email,
                org_slug=self.git_org.slug,
            )
        self.last_commit = sha
        return sha

    def ensure_repo(self, user: User) -> str | None:
        """Create the repository, holding the content as stored, unless there is one."""
        if self.last_commit:
            return None
        return self.record_version(user)

    @property
    def has_history(self) -> bool:
        """Whether this query's repository holds anything to read."""
        return bool(self.last_commit)

    def get_versions(self, page: int = 1, per_page: int = 20) -> dict:
        if not self.has_history:
            return {"items": [], "page": page}
        return {
            "items": self.client.get_commits(
                self.git_org.slug, self.repository, page=page, limit=per_page
            ),
            "page": page,
        }

    def get_version_content(self, ref: str = "main") -> str:
        """Return the SQL as of `ref`. Raises GitFileNotFound for an unknown ref."""
        raw = self.client.get_file(
            self.repository, QUERY_FILE_PATH, ref=ref, org_slug=self.git_org.slug
        )
        return raw.decode("utf-8")

    def get_version_diff(self, ref: str) -> dict:
        raw = self.client.get_commit(self.git_org.slug, self.repository, ref)
        commit = raw.get("commit") or {}
        author = commit.get("author") or {}
        return {
            "id": raw.get("sha", ref),
            "message": (commit.get("message") or "").strip(),
            "author_name": author.get("name", ""),
            "author_email": author.get("email", ""),
            "date": author.get("date", ""),
            "raw_diff": self.client.get_commit_diff(
                self.git_org.slug, self.repository, ref
            ),
        }

    def update_if_has_perm(self, principal: User, **kwargs):
        if not principal.has_perm("data_studio.update_saved_query", self):
            raise PermissionDenied

        # Sharing is gated separately from the rest of the attributes, and only when
        # it actually changes: a client echoing back the current visibility must not
        # need the stricter permission.
        visibility = kwargs.get("visibility")
        if visibility is not None and visibility != self.visibility:
            if not principal.has_perm(
                "data_studio.update_saved_query_visibility", self
            ):
                raise PermissionDenied
            self.visibility = visibility

        content = kwargs.get("content")
        # Compared in the form `save` stores, since that is what the repository holds
        # too: content differing only by the characters sanitizing drops would otherwise
        # commit a version whose diff is empty.
        new_content = sanitize_sql(content) if content is not None else None
        content_changed = new_content is not None and new_content != self.content

        # Only the SQL is versioned, so renaming a query or resharing it records
        # nothing — there is no new version of the query to browse.
        with transaction.atomic():
            if content_changed:
                # Seeded with the content as stored, so a query older than versioning
                # keeps the version it had rather than starting its history at whichever
                # edit happened to come next.
                self.ensure_repo(principal)

            if kwargs.get("name") is not None:
                self.name = kwargs["name"]
            if new_content is not None:
                self.content = new_content
            # description is optional/blankable: an explicit null clears it, mirroring create.
            if "description" in kwargs:
                self.description = kwargs["description"] or ""

            if content_changed:
                self.record_version(principal, f"Update {self.name}")

            return self.save()

    def delete_if_has_perm(self, principal: User):
        if not principal.has_perm("data_studio.delete_saved_query", self):
            raise PermissionDenied

        with transaction.atomic():
            result = self.delete()
            if self.has_history:
                # Archived rather than deleted: the history outlives the query, as it
                # does for web apps. Deletions that bypass this method (a workspace or
                # an author going away) leave the repository behind — see the
                # organization-level archiving in `hexa.user_management`.
                self.archive_repo()
            return result


class QueryLogQuerySet(BaseQuerySet):
    def filter_for_user(self, user: AnonymousUser | UserInterface) -> models.QuerySet:
        return self._filter_for_user_and_query_object(
            user,
            models.Q(workspace__in=Workspace.objects.filter_for_user(user)),
        )


class QueryLog(Base):
    """Audit log entry for a query executed against a data source via the API."""

    # SQLSTATE code reported for a successfully completed statement
    # (https://www.postgresql.org/docs/current/errcodes-appendix.html)
    SQLSTATE_SUCCESS = "00000"

    class Status(models.TextChoices):
        SUCCESS = "SUCCESS"
        # The query reached the data source but failed (invalid SQL, timeout, ...)
        ERROR = "ERROR"
        # The user was not allowed to run queries against the target
        DENIED = "DENIED"
        # The query was rejected before reaching the data source (e.g. multiple statements)
        REJECTED = "REJECTED"
        # A streaming export still in flight: the entry is written when the stream starts
        # and only becomes SUCCESS/ERROR once it ends, so an entry left here means that
        # end was never observed — a cancelled download or a worker killed mid-stream.
        STREAMING = "STREAMING"

    class Origin(models.TextChoices):
        # The client did not identify itself; every query arrives through the API anyway
        OTHER = "OTHER"
        DATA_STUDIO = "DATA_STUDIO"
        # Set server-side by the CSV export view and never accepted from a client (see
        # schema.py), so it marks an actual full-result export rather than a claim
        DATA_STUDIO_EXPORT = "DATA_STUDIO_EXPORT"
        # Set server-side from the request, never accepted from a client: it is
        # the only origin that carries a security meaning (a web app can run
        # stored queries and nothing else).
        WEBAPP = "WEBAPP"

    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="query_logs"
    )
    # SET_NULL, unlike SavedQuery.created_by: a log entry is worth keeping even once
    # nobody is named on it, because what it answers ("how much was this workspace
    # queried, what failed") is about the workspace rather than the person. The SQL
    # text stays with it; dropping that is a retention decision about the audit trail
    # as a whole, not something the saved-query deletion policy should settle on its
    # own (see `saved_queries_on_author_deleted`).
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="query_logs",
    )
    query = models.TextField()
    # Set when the SQL came from a stored query rather than from the caller, so
    # the audit trail answers "which saved query ran" and not only "what SQL ran".
    saved_query = models.ForeignKey(
        SavedQuery,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="query_logs",
    )
    status = models.CharField(max_length=10, choices=Status.choices)
    # SQLSTATE error code (https://www.postgresql.org/docs/current/errcodes-appendix.html);
    # SQLSTATE_SUCCESS on success, null when the query never reached the data source
    result_code = models.CharField(max_length=5, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True)
    row_count = models.PositiveIntegerField(null=True)
    truncated = models.BooleanField(default=False)
    origin = models.CharField(
        max_length=20, choices=Origin.choices, default=Origin.OTHER
    )
    # Free-text identifier of what was queried (e.g. "workspace_database"),
    # kept as plain text rather than choices so new source types don't need a migration.
    target = models.TextField()

    objects = QueryLogQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["workspace", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["origin"]),
            models.Index(fields=["target"]),
        ]

    def __str__(self) -> str:
        return f"{self.workspace.slug} - {self.status} - {self.created_at:%Y-%m-%d %H:%M:%S}"
