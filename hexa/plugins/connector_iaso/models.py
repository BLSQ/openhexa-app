import typing
from datetime import datetime
from logging import getLogger

from django.contrib.auth.models import AnonymousUser
from django.db import models, transaction
from django.db.models import Q
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hexa.catalog.models import Datasource, Entry
from hexa.catalog.sync import DatasourceSyncResult
from hexa.core.models.base import BaseQuerySet
from hexa.core.models.cryptography import EncryptedTextField
from hexa.plugins.connector_iaso.api import get_forms_json
from hexa.user_management import models as user_management_models
from hexa.user_management.models import Permission

logger = getLogger(__name__)


class IASOAccountQuerySet(BaseQuerySet):
    def filter_for_user(
        self,
        user: typing.Union[AnonymousUser, user_management_models.User],
    ):
        if not user.is_authenticated:
            return self.none()
        elif user.is_superuser:
            queryset = self.all()
        else:
            queryset = self.filter(
                iasopermission__team__in=user.team_set.all()
            ).distinct()

        return queryset


class IASOAccount(Datasource):
    class Meta:
        verbose_name = "IASO Account"
        verbose_name_plural = "IASO Account"
        ordering = ("api_url",)

    objects = IASOAccountQuerySet.as_manager()

    name = models.TextField()
    api_url = models.URLField()
    username = EncryptedTextField()
    password = EncryptedTextField()

    def get_permission_set(self):
        return self.iasopermission_set.all()

    def sync(self):
        result = get_forms_json(iaso_account=self)

        with transaction.atomic():
            IASOAccount.objects.select_for_update().get(pk=self.pk)
            with transaction.atomic():
                created_count = 0
                updated_count = 0
                identical_count = 0
                deleted_count = 0

                remote = set()
                local = {x.iaso_id: x for x in self.iasoform_set.all()}

                for form in result:
                    key = form["id"]
                    remote.add(key)
                    if key in local:
                        if datetime.fromtimestamp(form.get("updated_at")).replace(
                            tzinfo=timezone.utc
                        ) == local[key].updated.replace(tzinfo=timezone.utc):
                            identical_count += 1
                        else:
                            updated_count += 1
                            local[key].update_from_json(form)
                            local[key].save()
                    else:
                        IASOForm.create_from_json(self, form)
                        created_count += 1

                # cleanup unmatched objects
                for key, obj in local.items():
                    if key not in remote:
                        deleted_count += 1
                        obj.delete()
                # Flag the datasource as synced
                self.last_synced_at = timezone.now()
                self.save()

        return DatasourceSyncResult(
            datasource=self,
            created=created_count,
            updated=updated_count,
            identical=identical_count,
            deleted=deleted_count,
        )

    @property
    def content_summary(self):
        count = self.iasoform_set.count()

        return (
            ""
            if count == 0
            else _("%(count)d object%(suffix)s")
            % {"count": count, "suffix": pluralize(count)}
        )

    def populate_index(self, index):
        index.last_synced_at = self.last_synced_at
        index.content = self.content_summary
        index.description = f"IASO Forms from {self.api_url}"
        index.path = [self.pk.hex]
        index.external_id = self.name
        index.external_name = self.name
        index.search = f"{self.name}"
        index.datasource_name = self.name
        index.datasource_id = self.id

    def get_absolute_url(self):
        return reverse(
            "connector_iaso:datasource_index", kwargs={"datasource_id": self.id}
        )

    @property
    def display_name(self):
        return self.name

    def __str__(self):
        return self.display_name


class IASOPermission(Permission):
    class Meta(Permission.Meta):
        verbose_name = "IASO Permission"

        constraints = [
            models.UniqueConstraint(
                "team",
                "iaso_account",
                name="iaso_unique_team",
            ),
            models.CheckConstraint(
                check=Q(team__isnull=False),
                name="iaso_permission_team_not_null",
            ),
        ]

    iaso_account = models.ForeignKey("IASOAccount", on_delete=models.CASCADE)

    def index_object(self):
        self.iaso_account.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on IASOAccount '{self.iaso_account}'"


class IASOEntry(Entry):
    class Meta:
        abstract = True

    iaso_id = models.IntegerField(unique=True, editable=False)
    name = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    iaso_account = models.ForeignKey("IASOAccount", null=True, on_delete=models.CASCADE)

    def get_permission_set(self):
        return self.iaso_account.iasopermission_set.all()


class IASOForm(IASOEntry):
    class Meta:
        verbose_name = "IASO Form"
        ordering = ("name",)

    searchable = True  # TODO: remove (see comment in datasource_index command)

    form_id = models.CharField(max_length=50, default="")
    version_id = models.CharField(null=True, max_length=20)
    file_uri = models.TextField(null=True)
    org_unit_types = models.JSONField(blank=True, default=dict)
    projects = models.JSONField(blank=True, default=dict)

    def populate_index(self, index):
        index.last_synced_at = self.iaso_account.last_synced_at
        index.external_name = self.name
        index.path = [self.iaso_account.pk.hex, self.pk.hex]
        index.external_id = self.name
        index.external_type = "Form"
        index.search = f"{self.name} {self.form_id}"
        index.datasource_name = self.iaso_account.name
        index.datasource_id = self.iaso_account.id

    @classmethod
    def cleanup_json_projects(cls, data):
        for p in data:
            if "feature_flags" in p:
                del p["feature_flags"]
        return data

    def update_from_json(self, metadata):
        self.name = metadata["name"]
        self.created = datetime.fromtimestamp(metadata["created_at"]).replace(
            tzinfo=timezone.utc
        )
        self.updated = datetime.fromtimestamp(metadata["updated_at"]).replace(
            tzinfo=timezone.utc
        )
        self.form_id = metadata["form_id"]
        self.version_id = (
            metadata["latest_form_version"].get("version_id", "")
            if metadata.get("latest_form_version")
            else ""
        )
        self.file_uri = (
            metadata["latest_form_version"].get("file", "")
            if metadata.get("latest_form_version")
            else ""
        )
        self.org_unit_types = metadata["org_unit_types"]
        self.projects = self.cleanup_json_projects(metadata["projects"])

    @classmethod
    def create_from_json(cls, iaso_account, metadata):
        return cls.objects.create(
            iaso_account=iaso_account,
            iaso_id=metadata["id"],
            name=metadata["name"],
            created=datetime.fromtimestamp(metadata["created_at"]).replace(
                tzinfo=timezone.utc
            ),
            updated=datetime.fromtimestamp(metadata["updated_at"]).replace(
                tzinfo=timezone.utc
            ),
            form_id=metadata["form_id"],
            version_id=metadata["latest_form_version"].get("version_id", "")
            if metadata.get("latest_form_version")
            else "",
            file_uri=metadata["latest_form_version"].get("file", "")
            if metadata.get("latest_form_version")
            else "",
            org_unit_types=metadata["org_unit_types"],
            projects=cls.cleanup_json_projects(metadata["projects"]),
        )

    def get_absolute_url(self):
        return reverse(
            "connector_iaso:iasoform_detail",
            kwargs={"iasoaccount_id": self.iaso_account.id, "iaso_id": self.iaso_id},
        )

    @property
    def display_name(self):
        return self.name
