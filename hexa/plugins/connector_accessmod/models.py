import enum
import mimetypes

from django.db import models
from django_countries.fields import CountryField
from model_utils.managers import InheritanceManager, InheritanceQuerySet

from hexa.core.models import Base


class AccessmodQuerySet(models.QuerySet):
    def filter_for_user(self, user):
        raise NotImplementedError(
            "Catalog querysets should implement the filter_for_user() method"
        )


class ProjectQuerySet(AccessmodQuerySet):
    def filter_for_user(self, user):
        return self.filter(owner=user)


class Project(Base):
    name = models.TextField()
    country = CountryField()
    owner = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    spatial_resolution = models.PositiveIntegerField()
    crs = models.PositiveIntegerField()

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]


class FilesetQuerySet(AccessmodQuerySet):
    def filter_for_user(self, user):
        return self.filter(owner=user)


class Fileset(Base):
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    name = models.TextField()
    role = models.ForeignKey("FilesetRole", on_delete=models.PROTECT)
    owner = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )

    objects = FilesetQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]


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
    name = models.TextField()
    code = models.CharField(max_length=50, choices=FilesetRoleCode.choices)
    format = models.CharField(max_length=20, choices=FilesetFormat.choices)

    class Meta:
        ordering = ["code"]


class FileQuerySet(AccessmodQuerySet):
    def filter_for_user(self, user):
        return self.filter(fileset__owner=user)


class File(Base):
    mime_type = models.CharField(
        max_length=255
    )  # According to the spec https://datatracker.ietf.org/doc/html/rfc4288#section-4.2
    uri = models.TextField()
    fileset = models.ForeignKey("Fileset", on_delete=models.CASCADE)
    objects = FileQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]


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


class AnalysisQuerySet(AccessmodQuerySet, InheritanceQuerySet):
    def filter_for_user(self, user):
        return self.filter(owner=user)


class AnalysisManager(InheritanceManager):
    """Unfortunately, InheritanceManager does not support from_queryset, so we have to subclass it
    and "re-attach" the queryset methods ourselves"""

    def get_queryset(self):
        return AnalysisQuerySet(self.model)

    def filter_for_user(self, user):
        return self.get_queryset().filter_for_user(user)


class Analysis(Base):
    project = models.ForeignKey("Project", on_delete=models.PROTECT)
    owner = models.ForeignKey(
        "user_management.User", null=True, on_delete=models.SET_NULL
    )
    status = models.CharField(
        max_length=50, choices=AnalysisStatus.choices, default=AnalysisStatus.DRAFT
    )
    name = models.TextField()

    objects = AnalysisManager()

    def save(self, *args, **kwargs):
        if self.status == AnalysisStatus.DRAFT:
            self.update_status_if_draft()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.status in [AnalysisStatus.QUEUED, AnalysisStatus.RUNNING]:
            raise ValueError(f"Cannot delete analyses in {self.status} state")
        return super().delete(*args, **kwargs)

    def run(self):
        if self.status != AnalysisStatus.READY:
            raise ValueError(f"Cannot run analyses in {self.status} state")
        self.status = AnalysisStatus.QUEUED
        self.save()

    @property
    def type(self) -> AnalysisType:
        raise NotImplementedError

    def update_status_if_draft(self):
        raise NotImplementedError

    def set_outputs(self, **kwargs):
        raise NotImplementedError

    class Meta:
        ordering = ["-created_at"]


class AccessibilityAnalysis(Analysis):
    extent = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, related_name="+"
    )
    land_cover = models.ForeignKey(
        "Fileset", on_delete=models.PROTECT, null=True, related_name="+"
    )
    dem = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    transport_network = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    slope = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    water = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    barrier = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    moving_speeds = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    health_facilities = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    anisotropic = models.BooleanField(default=True)
    invert_direction = models.BooleanField(default=False)
    max_travel_time = models.IntegerField(null=True, default=360)

    travel_times = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    friction_surface = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )

    def update_status_if_draft(self):
        if all(
            value is not None
            for value in [
                getattr(self, field)
                for field in [
                    "name",
                    "extent",
                    "land_cover",
                    "transport_network",
                    "slope",
                    "water",
                    "health_facilities",
                ]
            ]
        ):
            self.status = AnalysisStatus.READY

    def set_outputs(self, travel_times: str, friction_surface: str):
        self.travel_times = Fileset.objects.create(
            project=self.project,
            name="Travel times",
            role=FilesetRole.objects.get(code=FilesetRoleCode.TRAVEL_TIMES),
            owner=self.owner,
        )
        self.travel_times.file_set.create(
            mime_type=mimetypes.guess_type(travel_times), uri=travel_times
        )
        self.friction_surface = Fileset.objects.create(
            project=self.project,
            name="Friction surface",
            role=FilesetRole.objects.get(code=FilesetRoleCode.FRICTION_SURFACE),
            owner=self.owner,
        )
        self.friction_surface.file_set.create(
            mime_type=mimetypes.guess_type(friction_surface), uri=friction_surface
        )
        self.save()

    @property
    def type(self) -> AnalysisType:
        return AnalysisType.ACCESSIBILITY


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

    def set_outputs(self, geographic_coverage: str, catchment_areas: str):
        self.geographic_coverage = Fileset.objects.create(
            project=self.project,
            name="Geographic coverage",
            role=FilesetRole.objects.get(code=FilesetRoleCode.COVERAGE),
            owner=self.owner,
        )
        self.geographic_coverage.file_set.create(
            mime_type=mimetypes.guess_type(geographic_coverage),
            uri=geographic_coverage,
        )
        self.catchment_areas = Fileset.objects.create(
            project=self.project,
            name="Catchment areas",
            role=FilesetRole.objects.get(code=FilesetRoleCode.CATCHMENT_AREAS),
            owner=self.owner,
        )
        self.catchment_areas.file_set.create(
            mime_type=mimetypes.guess_type(catchment_areas), uri=catchment_areas
        )
        self.save()

    @property
    def type(self) -> AnalysisType:
        return AnalysisType.GEOGRAPHIC_COVERAGE
