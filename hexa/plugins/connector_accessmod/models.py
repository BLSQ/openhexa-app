import enum
import typing

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.db.models import Q
from django.http import HttpRequest
from django_countries.fields import CountryField
from model_utils.managers import InheritanceManager, InheritanceQuerySet

from hexa.catalog.models import Datasource, Entry
from hexa.core import mimetypes
from hexa.core.models import Base, Permission
from hexa.core.models.base import BaseQuerySet
from hexa.pipelines.models import Pipeline
from hexa.plugins.connector_airflow.models import DAG, DAGRunState
from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import Team, User


class ProjectQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user,
            Q(owner=user)
            | Q(projectpermission__team__in=Team.objects.filter_for_user(user)),
            return_all_if_superuser=False,
        )


class Project(Datasource):
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint("name", "owner", name="project_unique_name_owner")
        ]

    name = models.TextField(verbose_name="project name")
    country = CountryField()
    owner = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    spatial_resolution = models.PositiveIntegerField()
    crs = models.PositiveIntegerField()
    extent = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )

    objects = ProjectQuerySet.as_manager()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        """We override delete() here because we can't control Django CASCADE order. Foreign keys from Analysis to
        Fileset are PROTECTED, which prevents a simple CASCADE delete at the project level."""

        self.analysis_set.all().delete()

        return super().delete(*args, **kwargs)

    @property
    def display_name(self):
        return self.name

    def sync(self):
        pass  # No need to sync, source of truth is OpenHexa

    def get_pipeline_credentials(self):
        pass

    def get_permission_set(self):
        return self.projectpermission_set.all()

    def populate_index(self, index):
        raise NotImplementedError  # Skip indexing for now

    def get_absolute_url(self):
        raise NotImplementedError

    def __str__(self):
        return self.name


class ProjectPermission(Permission):
    project = models.ForeignKey("connector_accessmod.Project", on_delete=models.CASCADE)

    class Meta:
        unique_together = [("project", "team")]

    def index_object(self):
        self.project.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on AM project '{self.project}'"


class FilesetQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.filter(project__in=Project.objects.filter_for_user(user)).distinct()


class Fileset(Entry):
    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                "name", "project", name="fileset_unique_name_project"
            )
        ]

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    name = models.TextField()
    role = models.ForeignKey("FilesetRole", on_delete=models.PROTECT)
    owner = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )

    objects = FilesetQuerySet.as_manager()

    def get_permission_set(self):
        return self.project.get_permission_set()

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError


class FilesetFormat(models.TextChoices):
    VECTOR = "VECTOR"
    RASTER = "RASTER"
    TABULAR = "TABULAR"


class FilesetRoleCode(models.TextChoices):
    BARRIER = "BARRIER"
    CATCHMENT_AREAS = "CATCHMENT_AREAS"
    COVERAGE = "COVERAGE"
    DEM = "DEM"
    FRICTION_SURFACE = "FRICTION_SURFACE"
    GEOMETRY = "GEOMETRY"
    HEALTH_FACILITIES = "HEALTH_FACILITIES"
    LAND_COVER = "LAND_COVER"
    MOVING_SPEEDS = "MOVING_SPEEDS"
    POPULATION = "POPULATION"
    SLOPE = "SLOPE"
    TRANSPORT_NETWORK = "TRANSPORT_NETWORK"
    TRAVEL_TIMES = "TRAVEL_TIMES"
    WATER = "WATER"


class FilesetRole(Base):
    class Meta:
        ordering = ["code"]

    name = models.TextField()
    code = models.CharField(max_length=50, choices=FilesetRoleCode.choices)
    format = models.CharField(max_length=20, choices=FilesetFormat.choices)


class FileQuerySet(BaseQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.filter(fileset__in=Fileset.objects.filter_for_user(user)).distinct()


class File(Entry):
    class Meta:
        ordering = ["-created_at"]

    mime_type = models.CharField(
        max_length=255
    )  # According to the spec https://datatracker.ietf.org/doc/html/rfc4288#section-4.2
    uri = models.TextField(unique=True)
    fileset = models.ForeignKey("Fileset", on_delete=models.CASCADE)
    objects = FileQuerySet.as_manager()

    def get_permission_set(self):
        return self.fileset.get_permission_set()

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    @property
    def name(self):
        return self.uri.split("/")[-1]


class AnalysisStatus(models.TextChoices):
    DRAFT = "DRAFT"
    READY = "READY"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class AnalysisType(str, enum.Enum):
    ACCESSIBILITY = "ACCESSIBILITY"
    GEOGRAPHIC_COVERAGE = "GEOGRAPHIC_COVERAGE"


class AnalysisQuerySet(BaseQuerySet, InheritanceQuerySet):
    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self._filter_for_user_and_query_object(
            user,
            Q(owner=user)
            | Q(analysispermission__team__in=Team.objects.filter_for_user(user)),
            return_all_if_superuser=False,
        )


class AnalysisManager(InheritanceManager):
    """Unfortunately, InheritanceManager does not support from_queryset, so we have to subclass it
    and "re-attach" the queryset methods ourselves."""

    def get_queryset(self):
        return AnalysisQuerySet(self.model)

    def filter_for_user(self, user: typing.Union[AnonymousUser, User]):
        return self.get_queryset().filter_for_user(user)


class Analysis(Pipeline):
    """Base analysis class

    NOTE: This model is impacted by a signal (see signals.py in the current module)
    Whenever a DAGRun linked to an analysis has a new state, the analysis status is likely to change.
    (see also the update_status_from_dag_run_state() method of this class)
    """

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                "name", "project", name="analysis_unique_name_project"
            )
        ]

    DAG_RUN_STATE_MAPPINGS = {
        DAGRunState.QUEUED: AnalysisStatus.QUEUED,
        DAGRunState.RUNNING: AnalysisStatus.RUNNING,
        DAGRunState.SUCCESS: AnalysisStatus.SUCCESS,
        DAGRunState.FAILED: AnalysisStatus.FAILED,
    }
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    owner = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=50, choices=AnalysisStatus.choices, default=AnalysisStatus.DRAFT
    )
    name = models.TextField()
    dag_run = models.ForeignKey(
        "connector_airflow.DAGRun",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )

    objects = AnalysisManager()

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    def get_permission_set(self):
        return self.analysispermission_set.all()

    def save(self, *args, **kwargs):
        if self.status == AnalysisStatus.DRAFT:
            self.update_status_if_draft()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status in [AnalysisStatus.QUEUED, AnalysisStatus.RUNNING]:
            raise ValueError(f"Cannot delete analyses in {self.status} state")
        return super().delete(*args, **kwargs)

    @transaction.atomic
    def run(
        self,
        *,
        request: HttpRequest,
        conf: typing.Mapping[str, typing.Any] = None,
        webhook_path: str = None,
    ):
        if self.status != AnalysisStatus.READY:
            raise ValueError(f"Cannot run analyses in {self.status} state")

        dag = DAG.objects.get(dag_id=self.dag_id)

        # This is a temporary solution until we figure out storage requirements
        if settings.ACCESSMOD_S3_BUCKET_NAME is None:
            raise ValueError("ACCESSMOD_S3_BUCKET_NAME is not set")
        try:
            bucket = Bucket.objects.get(name=settings.ACCESSMOD_S3_BUCKET_NAME)
        except Bucket.DoesNotExist:
            raise ValueError(
                f"The {settings.ACCESSMOD_S3_BUCKET_NAME} bucket does not exist"
            )

        self.dag_run = dag.run(
            request=request,
            conf=self.build_dag_conf(
                {
                    "output_dir": f"s3://{bucket.name}/{self.project.id}/{self.id}/",
                }
            ),
            webhook_path=webhook_path,
        )

        self.status = AnalysisStatus.QUEUED
        self.save()

    @property
    def type(self) -> AnalysisType:
        raise NotImplementedError

    @property
    def dag_id(self):
        raise NotImplementedError

    def build_dag_conf(self, conf: typing.Mapping[str, typing.Any]):
        raise NotImplementedError

    def update_status_if_draft(self):
        raise NotImplementedError

    def update_status(self, status: AnalysisStatus):
        if self.status in [status, AnalysisStatus.SUCCESS, AnalysisStatus.FAILED]:
            # If no status change or already successful or failed, do nothing
            return
        elif (
            self.status == AnalysisStatus.QUEUED
            and status
            in [AnalysisStatus.RUNNING, AnalysisStatus.SUCCESS, AnalysisStatus.FAILED]
        ) or (
            self.status == AnalysisStatus.RUNNING
            and status in [AnalysisStatus.SUCCESS, AnalysisStatus.FAILED]
        ):
            self.status = status
            self.save()
        else:
            raise ValueError(f"Cannot change status from {self.status} to {status}")

    def update_status_from_dag_run_state(self, state: DAGRunState):
        try:
            new_status_candidate = self.DAG_RUN_STATE_MAPPINGS[state]
            if new_status_candidate != self.status:
                self.update_status(self.DAG_RUN_STATE_MAPPINGS[state])
        except KeyError:
            raise ValueError(f"Cannot map DAGRunState {state}")

    @staticmethod
    def input_path(input_fileset: typing.Optional[Fileset] = None):
        if input_fileset is None:
            return None

        return (
            input_fileset.file_set.first().uri
        )  # TODO: handle exceptions and multi-files filesets

    def set_outputs(self, **kwargs):
        raise NotImplementedError

    def set_output(
        self,
        *,
        output_key: str,
        output_role_code: FilesetRoleCode,
        output_name: str,
        output_value: str,
    ):
        setattr(
            self,
            output_key,
            Fileset.objects.create(
                project=self.project,
                name=f"{output_name} ({self.name})",
                role=FilesetRole.objects.get(code=output_role_code),
                owner=self.owner,
            ),
        )
        getattr(self, output_key).file_set.create(
            mime_type=mimetypes.guess_type(output_value)[0], uri=output_value
        )
        self.save()


class AnalysisPermission(Permission):
    analysis = models.ForeignKey(
        "connector_accessmod.Analysis", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = [("analysis", "team")]

    def index_object(self):
        self.analysis.build_index()

    def __str__(self):
        return f"Permission for team '{self.team}' on AM analysis '{self.analysis}'"


class AccessibilityAnalysisAlgorithm(models.TextChoices):
    ANISOTROPIC = "ANISOTROPIC"
    ISOTROPIC = "ISOTROPIC"


class AccessibilityAnalysis(Analysis):
    class Meta:
        verbose_name_plural = "Accessibility analyses"

    land_cover = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    dem = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    transport_network = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    slope = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    water = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    barrier = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    moving_speeds = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    health_facilities = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    invert_direction = models.BooleanField(default=False)
    max_travel_time = models.IntegerField(default=360)
    max_slope = models.FloatField(null=True, blank=True)
    priority_roads = models.BooleanField(default=True)
    priority_land_cover = ArrayField(models.PositiveSmallIntegerField(), default=list)

    water_all_touched = models.BooleanField(default=True)
    algorithm = models.CharField(
        max_length=50,
        choices=AccessibilityAnalysisAlgorithm.choices,
        default=AccessibilityAnalysisAlgorithm.ANISOTROPIC,
    )
    knight_move = models.BooleanField(default=False)

    travel_times = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    friction_surface = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    catchment_areas = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    def update_status_if_draft(self):
        if all(
            value is not None
            for value in [
                getattr(self, field)
                for field in [
                    "name",
                    "land_cover",
                    "transport_network",
                    "slope",
                    "water",
                    "health_facilities",
                ]
            ]
        ):
            self.status = AnalysisStatus.READY

    @transaction.atomic
    def set_outputs(
        self, travel_times: str, friction_surface: str, catchment_areas: str
    ):
        self.set_output(
            output_key="travel_times",
            output_role_code=FilesetRoleCode.TRAVEL_TIMES,
            output_name="Travel times",
            output_value=travel_times,
        )
        self.set_output(
            output_key="friction_surface",
            output_role_code=FilesetRoleCode.FRICTION_SURFACE,
            output_name="Friction surface",
            output_value=friction_surface,
        )
        self.set_output(
            output_key="catchment_areas",
            output_role_code=FilesetRoleCode.CATCHMENT_AREAS,
            output_name="Catchment areas",
            output_value=catchment_areas,
        )

    @property
    def type(self) -> AnalysisType:
        return AnalysisType.ACCESSIBILITY

    @property
    def dag_id(self):
        return "am_accessibility"

    def build_dag_conf(self, base_config: typing.Mapping[str, typing.Any]):
        dag_conf = {
            **base_config,
            "algorithm": self.algorithm,
            # "category_column": "???",   # TODO: add
            "max_travel_time": self.max_travel_time,
            "priority_roads": self.priority_roads,
            "water_all_touched": self.water_all_touched,
            "knight_move": self.knight_move,
            "invert_direction": self.invert_direction,
            "overwrite": False,
        }

        for fileset_field in [
            "health_facilities",
            "dem",
            "slope",
            "land_cover",
            "transport_network",
            "barrier",
            "water",
            "moving_speeds",
        ]:
            field_value = getattr(self, fileset_field)
            if field_value is not None:
                dag_conf[fileset_field] = self.input_path(field_value)

        if self.max_slope is not None:
            dag_conf["max_slope"] = self.max_slope
        if len(self.priority_land_cover) > 0:
            dag_conf["priority_land_cover"] = ",".join(
                [str(p) for p in self.priority_land_cover]
            )

        return dag_conf


class GeographicCoverageAnalysis(Analysis):
    population = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    friction_surface = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    dem = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    health_facilities = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    anisotropic = models.BooleanField(default=True)
    max_travel_time = models.IntegerField(null=True, default=360)
    hf_processing_order = models.CharField(max_length=100)

    geographic_coverage = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    catchment_areas = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )

    def populate_index(self, index):
        raise NotImplementedError

    def get_absolute_url(self):
        raise NotImplementedError

    def update_status_if_draft(self):
        if all(
            value is not None
            for value in [
                getattr(self, field)
                for field in [
                    "name",
                    "population",
                    "friction_surface",
                    "dem",
                    "health_facilities",
                    "hf_processing_order",
                ]
            ]
        ):
            self.status = AnalysisStatus.READY

    @transaction.atomic
    def set_outputs(self, geographic_coverage: str, catchment_areas: str):
        self.set_output(
            output_key="geographic_coverage",
            output_role_code=FilesetRoleCode.COVERAGE,
            output_name="Geographic coverage",
            output_value=geographic_coverage,
        )
        self.set_output(
            output_key="catchment_areas",
            output_role_code=FilesetRoleCode.CATCHMENT_AREAS,
            output_name="Catchment areas",
            output_value=catchment_areas,
        )

    @property
    def type(self) -> AnalysisType:
        return AnalysisType.GEOGRAPHIC_COVERAGE

    @property
    def dag_id(self):
        return "am_geographic_coverage"

    def build_dag_conf(self, output_dir: str):
        raise NotImplementedError
