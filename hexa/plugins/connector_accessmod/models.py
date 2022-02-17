from django.db import models
from django_countries.fields import CountryField

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
    owner = models.ForeignKey("user_management.User", on_delete=models.PROTECT)
    spatial_resolution = models.PositiveIntegerField()

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["name"]


class FilesetQuerySet(AccessmodQuerySet):
    def filter_for_user(self, user):
        return self.filter(owner=user)


class Fileset(Base):
    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    name = models.TextField()
    role = models.ForeignKey("FilesetRole", on_delete=models.PROTECT)
    owner = models.ForeignKey("user_management.User", on_delete=models.PROTECT)

    objects = FilesetQuerySet.as_manager()

    class Meta:
        ordering = ["name"]


class FilesetFormat(models.TextChoices):
    VECTOR = "VECTOR"
    RASTER = "RASTER"
    TABULAR = "TABULAR"


class FilesetRoleCode(models.TextChoices):
    LAND_COVER = "LAND_COVER"
    DEM = "DEM"
    TRANSPORT_NETWORK = "TRANSPORT_NETWORK"
    SLOPE = "SLOPE"
    WATER = "WATER"
    BARRIER = "BARRIER"
    MOVING_SPEEDS = "MOVING_SPEEDS"
    HEALTH_FACILITIES = "HEALTH_FACILITIES"


class FilesetRole(Base):
    name = models.TextField()
    code = models.CharField(max_length=50, choices=FilesetRoleCode.choices)
    format = models.CharField(max_length=20, choices=FilesetFormat.choices)

    class Meta:
        ordering = ["name"]


class FileQuerySet(AccessmodQuerySet):
    def filter_for_user(self, user):
        return self.filter(fileset__owner=user)


class File(Base):
    mime_type = models.CharField(max_length=50)
    uri = models.TextField()
    fileset = models.ForeignKey("Fileset", on_delete=models.CASCADE)
    objects = FileQuerySet.as_manager()


class AnalysisStatus(models.TextChoices):
    PENDING = "PENDING"
    READY = "READY"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Analysis(Base):
    status = models.CharField(
        max_length=50, choices=AnalysisStatus.choices, default=AnalysisStatus.PENDING
    )
    name = models.TextField()


class AccessibilityAnalysis(Analysis):
    extent = models.JSONField(null=True)
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
    anisotropic = models.BooleanField(null=True)
    max_travel_time = models.IntegerField(null=True)

    travel_times = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    friction_surface = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )


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
    anisotropic = models.BooleanField(null=True)
    max_travel_time = models.IntegerField(null=True)
    hf_processing_order = models.CharField(max_length=100)

    geographic_coverage = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
    catchment_areas = models.ForeignKey(
        "Fileset", null=True, on_delete=models.PROTECT, related_name="+"
    )
