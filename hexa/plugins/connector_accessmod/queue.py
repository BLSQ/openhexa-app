import os
import typing
from logging import getLogger

# Try to load datasciences dependencies
# if not present, deactivate validation
try:
    import geopandas as gpd
    import numpy as np
    import rasterio

    missing_dependencies = False
except ImportError:
    missing_dependencies = True

from dpq.queue import AtLeastOnceQueue

import hexa.plugins.connector_s3.api as s3_api
from hexa.plugins.connector_s3.models import Bucket

from .models import Fileset, FilesetRoleCode, FilesetStatus, ValidateFilesetJob

logger = getLogger(__name__)


def validate_geopkg(
    gdf: "gpd.GeoDataFrame", fileset: Fileset, geom_type: typing.List[str]
):
    # validate CRS
    if gdf.crs.to_epsg() != fileset.project.crs:
        fileset.set_invalid("wrong CRS")
        return

    # need data inside
    if len(gdf) == 0:
        fileset.set_invalid("empty dataset")
        return

    # validate data content
    if not gdf.is_valid.all():
        fileset.set_invalid("data containing invalid geometry")
        return

    # are all element inside df type Point, LineString, ...
    if not (gdf.geom_type.isin(geom_type)).all():
        fileset.set_invalid("data containing invalid geometry type")
        return

    # TODO: validate that each point inside project extend


def validate_raster(raster, fileset: Fileset):
    # validate CRS -> must be the same
    # NOTE: we should validate that CRS is in (m) in project
    if not raster.crs.is_epsg_code:
        fileset.set_invalid("wrong CRS, not epsg")
        return

    if int(raster.crs.to_epsg()) != fileset.project.crs:
        fileset.set_invalid("wrong CRS")
        return

    # validate spatial resolution
    if int(raster.transform.a) != fileset.project.spatial_resolution:
        fileset.set_invalid("wrong spatial resolution")
        return

    # TODO: validate bounds
    # if raster.bounds != fileset.project.extend.metadata: i guess
    #     fileset.set_invalid("wrong extend")
    #     return


def validate_health_facilities(fileset: Fileset, filename: str):
    facilities = gpd.read_file(filename)
    validate_geopkg(facilities, fileset, ("Point",))

    if fileset.status == FilesetStatus.VALIDATING:
        # not invalid by previous checks
        fileset.status = FilesetStatus.VALID
        fileset.save()


def validate_water(fileset: Fileset, filename: str):
    water = gpd.read_file(filename)
    validate_geopkg(water, fileset, ("LineString", "MultiPolygon"))

    if fileset.status == FilesetStatus.VALIDATING:
        # not invalid by previous checks
        fileset.status = FilesetStatus.VALID
        fileset.save()


def validate_transport(fileset: Fileset, filename: str):
    transport = gpd.read_file(filename)
    validate_geopkg(transport, fileset, ("LineString",))

    if fileset.status == FilesetStatus.INVALID:
        # invalid by previous checks
        return

    # extract roads categories & validate
    if fileset.metadata is None:
        fileset.metadata = {}
    fileset.metadata["category_column"] = sorted(transport.highway.unique())
    fileset.status = FilesetStatus.VALID
    fileset.save()


def validate_dem(fileset: Fileset, filename: str):
    dem = rasterio.open(filename)
    validate_raster(dem, fileset)

    if fileset.status == FilesetStatus.INVALID:
        # invalid by previous checks
        return

    # validate min/max/mean altitude. assume band 1
    # use masked because otherwise invalid value may occure
    dem_content = dem.read(1, masked=True)
    if (
        dem_content.min() < -500
        or dem_content.max() > 8900
        or dem_content.mean() > 5000
    ):
        fileset.set_invalid("file content outside of reality")
        return

    fileset.status = FilesetStatus.VALID
    fileset.save()


def validate_land_cover(fileset: Fileset, filename: str):
    landcover = rasterio.open(filename)
    validate_raster(landcover, fileset)

    if fileset.status == FilesetStatus.INVALID:
        # invalid by previous checks
        return

    # validate number of class. assume band 1
    # use masked because otherwise invalid value may occure
    lc_content = landcover.read(1, masked=True)
    lc_classes = np.unique(lc_content.data)
    if len(lc_classes) > 50 or lc_content.min() < 0:
        fileset.set_invalid("file content outside of reality")
        return

    # extract land cover classes for frontend
    if fileset.metadata is None:
        fileset.metadata = {}
    fileset.metadata["classes"] = sorted([int(i) for i in lc_classes])
    fileset.status = FilesetStatus.VALID
    fileset.save()


def validate_data_and_download(fileset: Fileset) -> str:
    # check if content is present
    if fileset.file_set.count() != 1:
        # no content -> invalid
        # shapefile, multiple file content -> invalid (FIXME)
        fileset.set_invalid("wrong number of file")
        return None
    file = fileset.file_set.first()

    # retreive content
    if not file.uri.startswith("s3://") and len(file.uri) > 6:
        # support only S3 for now
        fileset.set_invalid("wrong uri")
        return None

    bucket_name, *key_parts = file.uri[5:].split("/")
    try:
        bucket = Bucket.objects.get(name=bucket_name)
    except Bucket.DoesNotExist:
        fileset.set_invalid("bucket not found")
        return None

    object_key = "/".join(key_parts)
    # erase always the same file, make sure we don't consume too much ram
    local_name = "/tmp/current_work_file"
    s3_api.download_file(bucket=bucket, object_key=object_key, target=local_name)

    # is there data inside?
    if os.stat(local_name).st_size == 0:
        fileset.set_invalid("empty file")
        return None

    return local_name


def validate_fileset_job(queue, job) -> None:
    if missing_dependencies:
        logger.error("Validation deactivated, missing dependencies")
        return

    try:
        fileset = Fileset.objects.get(id=job.args["fileset_id"])

    except Fileset.DoesNotExist:
        logger.error("fileset %s not found", job.args["fileset_id"])
        return

    # start processing
    logger.info("Starting validation fileset %s", job.args["fileset_id"])
    fileset.status = FilesetStatus.VALIDATING
    fileset.save()

    filename = validate_data_and_download(fileset)
    if not filename:
        # previous error, abort processing
        logger.error(
            "fileset %s : %s",
            job.args["fileset_id"],
            fileset.metadata["validation_error"],
        )
        return

    # TODO: should we validate the mime type?

    fileset_role_validator = {
        FilesetRoleCode.DEM: validate_dem,
        FilesetRoleCode.HEALTH_FACILITIES: validate_health_facilities,
        FilesetRoleCode.WATER: validate_water,
        FilesetRoleCode.TRANSPORT_NETWORK: validate_transport,
        FilesetRoleCode.LAND_COVER: validate_land_cover,
    }
    if fileset.role.code not in fileset_role_validator:
        # no validator for that role -> validate the FS
        fileset.status = FilesetStatus.VALID
        fileset.save()
        logger.info("No validator for fileset %s", job.args["fileset_id"])
        return

    # custom validation by role
    fileset_role_validator[fileset.role.code](fileset, filename)
    logger.info("Completed validation fileset %s", job.args["fileset_id"])


class ValidateFilesetQueue(AtLeastOnceQueue):
    # override the default job model; our job model has a specific table name
    job_model = ValidateFilesetJob


# task queue for the connector_accessmod
# AtLeastOnceQueue + try/except: if the worker fail, restart the task. if the task fail, drop it + log
validate_fileset_queue = ValidateFilesetQueue(
    tasks={
        "validate_fileset": validate_fileset_job,
    },
    notify_channel="validate_fileset_queue",
)
