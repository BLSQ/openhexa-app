import typing
from logging import getLogger

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import Datasource
from hexa.core.models import Base
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.cryptography import EncryptedTextField
from hexa.user_management import models as user_management_models
from hexa.user_management.models import Permission, PermissionMode

logger = getLogger(__name__)


class Credentials(Base):
    """We actually only want one set of credentials.
    In the futur (= soon), these "principal" credentials will be then used
    to generate short-lived credentials with a tailored policy giving access
    only to the buckets that the user team can access"""

    class Meta:
        verbose_name = "GCS Credentials"
        verbose_name_plural = "GCS Credentials"
        ordering = ("service_account",)

    service_account = models.CharField(max_length=30)
    project_id = models.CharField(max_length=30)
    client_id = models.CharField(max_length=30)
    client_email = models.CharField(max_length=100)
    client_x509_cert_url = models.CharField(max_length=150)
    auth_uri = models.CharField(
        max_length=100, default="https://accounts.google.com/o/oauth2/auth"
    )
    token_uri = models.CharField(
        max_length=100, default="https://oauth2.googleapis.com/token"
    )
    auth_provider_x509_cert_url = models.CharField(
        max_length=100, default="https://www.googleapis.com/oauth2/v1/certs"
    )

    private_key_id = EncryptedTextField(max_length=50)
    private_key = EncryptedTextField()

    @property
    def display_name(self):
        return self.service_account


class BucketQuerySet(BaseQuerySet):
    def filter_for_user(
        self,
        user: typing.Union[AnonymousUser, user_management_models.User],
        mode: PermissionMode = None,
        mode__in: typing.Sequence[PermissionMode] = None,
    ):
        if mode is not None and mode__in is not None:
            raise ValueError('Please provide either "mode" or "mode_in" - not both')

        if user.is_superuser:
            return self
        else:
            return self.none()


class Bucket(Datasource):
    def get_permission_set(self):
        return self.gcsbucketpermission_set.all()

    class Meta:
        verbose_name = "GCS Bucket"
        ordering = ("name",)

    name = models.CharField(max_length=200)

    objects = BucketQuerySet.as_manager()
    searchable = True

    @property
    def principal_credentials(self):
        try:
            return Credentials.objects.get()
        except (Credentials.DoesNotExist, Credentials.MultipleObjectsReturned):
            raise ValidationError(
                "The GCS connector plugin should be configured with a single Credentials entry"
            )

    @property
    def content_summary(self):
        count = 0

        return (
            ""
            if count == 0
            else _("%(count)d object%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )

    def populate_index(self, index):
        index.last_synced_at = self.last_synced_at
        index.content = self.content_summary
        index.path = [self.pk.hex]
        index.external_id = self.name
        index.external_name = self.name
        index.external_type = "bucket"
        index.search = f"{self.name}"
        index.datasource_name = self.name
        index.datasource_id = self.id

    @property
    def display_name(self):
        return self.name

    def __str__(self):
        return self.display_name

    def writable_by(self, user):
        if not user.is_authenticated:
            return False
        elif user.is_superuser:
            return True
        elif (
            GCSBucketPermission.objects.filter(
                bucket=self,
                team_id__in=user.team_set.all().values("id"),
                mode=PermissionMode.EDITOR,
            ).count()
            > 0
        ):
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse(
            "connector_gcs:datasource_detail", kwargs={"datasource_id": self.id}
        )


class GCSBucketPermission(Permission):
    class Meta(Permission.Meta):
        verbose_name = "Bucket Permission"

        constraints = [
            models.UniqueConstraint(
                "team",
                "bucket",
                name="gcs_bucket_unique_team",
                condition=Q(team__isnull=False),
            ),
            models.UniqueConstraint(
                "user",
                "bucket",
                name="gcs_bucket_unique_user",
                condition=Q(user__isnull=False),
            ),
            models.CheckConstraint(
                check=Q(team__isnull=False) | Q(user__isnull=False),
                name="gcs_bucket_permission_user_or_team_not_null",
            ),
        ]

    bucket = models.ForeignKey("Bucket", on_delete=models.CASCADE)

    def index_object(self):
        self.bucket.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on bucket '{self.bucket}'"
