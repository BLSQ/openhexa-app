import math
import os
from logging import getLogger

# Try to load datasciences dependencies
# if not present, deactivate validation
try:
    import geopandas as gpd
    import numpy as np
    import pandas as pd
    import pyproj
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.io import MemoryFile
    from rasterio.warp import calculate_default_transform, reproject
    from rio_cogeo.cogeo import cog_translate
    from rio_cogeo.profiles import cog_profiles

    missing_dependencies = False
except ImportError:
    missing_dependencies = True

from django.db import models
from dpq.queue import AtMostOnceQueue

import hexa.plugins.connector_s3.api as s3_api
from hexa.plugins.connector_s3.models import Bucket as S3Bucket

from .models import (
    Analysis,
    AnalysisStatus,
    Fileset,
    FilesetFormat,
    FilesetRoleCode,
    FilesetStatus,
    ValidateFilesetJob,
)

logger = getLogger(__name__)


def get_bucket_name(uri: str) -> str:
    # extract bucketname, assume a s3://path/file URI
    bucket_name, *key_parts = uri.split("://")[1].split("/")
    return bucket_name


def get_object_key(uri: str) -> str:
    # extract object key, assume a s3://path/file URI
    bucket_name, *key_parts = uri.split("://")[1].split("/")
    return "/".join(key_parts)


def get_base_dir(uri: str) -> str:
    # extract what could be the base dirname of a filename
    if "/" in uri:
        uri = "/".join(uri.split("/")[:-1])
    return uri.rstrip("/")


def get_main_filename(uri: str) -> str:
    # extract what could be the main part of a filename
    # split by '/' and keep the last part
    # split by '.' and drop what could be the extension
    if "/" in uri:
        filename = uri.split("/")[-1]
    else:
        filename = uri
    if "." in filename:
        filename = ".".join(filename.split(".")[:-1])
    return filename


def validate_geopkg(fileset: Fileset, filename: str):
    # open the content
    gdf = gpd.read_file(filename)

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

    geom_types = {
        FilesetRoleCode.HEALTH_FACILITIES: ("Point",),
        FilesetRoleCode.WATER: ("LineString", "MultiLineString", "MultiPolygon"),
        FilesetRoleCode.TRANSPORT_NETWORK: ("LineString", "MultiLineString"),
    }

    if fileset.role in geom_types:
        # are all element inside df type Point, LineString, ...
        if not (gdf.geom_type.isin(geom_types[fileset.role])).all():
            fileset.set_invalid("data containing invalid geometry type")
            return

    # TODO: validate that each point inside project extend
    return gdf


def validate_raster(fileset: Fileset, filename: str):
    # open content
    raster = rasterio.open(filename)

    # validate CRS -> must be the same
    # NOTE: we should validate that CRS is in (m) in project
    if fileset.role.code != FilesetRoleCode.POPULATION:
        # population can have any CRS, reprojected anyway
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
    return raster


def validate_transport(fileset: Fileset, transport: gpd.GeoDataFrame):
    # also extract metadata
    cols = sorted(transport.columns.to_list())
    cols.remove("geometry")
    col_values = {}
    for col in cols:
        # save some unique values for all columns, front can choose what it wants
        # truncate to max 20 elements
        # FIXME: will fail for weird python scalar like datetime, timedelta etc
        # which are not json encodable
        values = transport.get(col).unique()[:20].tolist()
        col_values[col] = sorted(filter(lambda v: not pd.isna(v), values))

    # extract roads categories & validate
    fileset.refresh_from_db()
    if fileset.metadata is None:
        fileset.metadata = {}

    fileset.metadata["columns"] = cols
    fileset.metadata["values"] = col_values
    fileset.metadata["length"] = len(transport)
    fileset.save()


def validate_continous_raster(fileset: Fileset, raster, extra_validation=None):
    # validate min/max/mean altitude. assume band 1
    # use masked because otherwise invalid value may occure
    raster_content = raster.read(1, masked=True)
    if extra_validation:
        extra_validation(fileset, raster, raster_content)
        if fileset.status == FilesetStatus.INVALID:
            return

    fileset.refresh_from_db()
    if fileset.metadata is None:
        fileset.metadata = {}

    fileset.metadata["min"] = int(raster_content.min())
    fileset.metadata["max"] = int(raster_content.max())
    if raster.nodata is None:
        fileset.metadata["nodata"] = None
    elif math.isnan(raster.nodata):
        fileset.set_invalid("Raster no data value cannot be NaN.")
        return
    else:
        fileset.metadata["nodata"] = int(raster.nodata)

    percentile = np.percentile(a=raster_content.compressed(), q=[1, 2, 98, 99])
    fileset.metadata["1p"] = float(percentile[0])
    fileset.metadata["2p"] = float(percentile[1])
    fileset.metadata["98p"] = float(percentile[2])
    fileset.metadata["99p"] = float(percentile[3])
    fileset.save()


def validate_dem(fileset: Fileset, dem):
    def validate_altitude(fileset, dem, dem_content):
        if (
            dem_content.min() < -500
            or dem_content.max() > 8900
            or dem_content.mean() > 5000
        ):
            fileset.set_invalid("file content outside of reality")
            return

    return validate_continous_raster(fileset, dem, validate_altitude)


def validate_positive_raster(fileset, raster):
    def validate_values(fileset, raster, raster_content):
        if raster_content.min() < -1:
            fileset.set_invalid("file content outside of reality")
            return

    return validate_continous_raster(fileset, raster, validate_values)


def validate_facilities(fileset: Fileset, facilities: gpd.GeoDataFrame):
    fileset.refresh_from_db()
    if fileset.metadata is None:
        fileset.metadata = {}

    fileset.metadata["length"] = len(facilities)
    fileset.save()


def validate_water(fileset: Fileset, water: gpd.GeoDataFrame):
    fileset.refresh_from_db()
    if fileset.metadata is None:
        fileset.metadata = {}

    fileset.metadata["length"] = len(water)
    fileset.save()


def validate_land_cover(fileset: Fileset, landcover):
    # validate number of class. assume band 1
    # use masked because otherwise invalid value may occure
    lc_content = landcover.read(1, masked=True)
    lc_classes = np.unique(lc_content.data)
    if len(lc_classes) > 50 or lc_content.min() < 0:
        fileset.set_invalid("file content outside of reality")
        return

    # extract land cover classes for frontend
    fileset.refresh_from_db()
    if fileset.metadata is None:
        fileset.metadata = {}
    fileset.metadata["unique_values"] = sorted([int(i) for i in lc_classes])
    if landcover.nodata is None:
        fileset.metadata["nodata"] = None
    else:
        fileset.metadata["nodata"] = landcover.nodata
    fileset.save()


def validate_stack(fileset: Fileset, stack):
    # validate number of class. assume band 1
    # use masked because otherwise invalid value may occure
    stack_content = stack.read(1, masked=True)
    stack_classes = np.unique(stack_content.data)
    if len(stack_classes) > 50 or stack_content.min() < 0:
        fileset.set_invalid("file content outside of reality")
        return

    # extract stack classes for frontend
    fileset.refresh_from_db()
    if fileset.metadata is None:
        fileset.metadata = {}
    fileset.metadata["unique_values"] = sorted([int(i) for i in stack_classes])
    if stack.nodata is None:
        fileset.metadata["nodata"] = None
    else:
        fileset.metadata["nodata"] = stack.nodata
    fileset.save()


def generate_geojson(fileset: Fileset, filename: str, **options):
    # Generate a GeoJSON copy from a fileset. change CRS if needed
    # used by frontend

    # maybe we need to copy the file? somehow it seems to lock the GPKG
    # target crs is epsg:4326 in dataviz
    viz_crs = pyproj.CRS.from_epsg(4326)
    gdf = gpd.read_file(filename)

    # set default crs
    if not gdf.crs:
        gdf.crs = viz_crs

    # reproject if needed
    if gdf.crs != viz_crs:
        _gdf = gdf.to_crs(viz_crs)
        del gdf  # liberate memory asap
        gdf = _gdf

    # rewrite to file in all case to force use geojson
    # usually input are in gpkg
    json_filename = "/tmp/current_work_file.geojson"
    gdf.to_file(json_filename, driver="GeoJSON")

    # upload to target!
    src_filename = fileset.file_set.first().uri
    dst_path = (
        get_object_key(get_base_dir(src_filename))
        + "/"
        + get_main_filename(src_filename)
        + "_viz.geojson"
    )

    uri_protocol = src_filename.split("://")[0]
    if uri_protocol == "s3":
        Bucket = S3Bucket
        upload_file = s3_api.upload_file

    bucket = Bucket.objects.get(name=get_bucket_name(src_filename))
    upload_file(bucket=bucket, object_key=dst_path, src_path=json_filename)
    fileset.refresh_from_db()
    fileset.visualization_uri = f"{uri_protocol}://{bucket.name}/{dst_path}"
    fileset.save()


def generate_cog_raster(fileset: Fileset, filename: str, **options):
    # 1) Open file & reproject to epsg 4326 in memory
    src = rasterio.open(filename)
    src_crs = src.crs
    crs = rasterio.crs.CRS({"init": "epsg:4326"})
    transform, width, height = calculate_default_transform(
        src_crs, crs, src.width, src.height, *src.bounds
    )
    kwargs = src.meta.copy()
    kwargs.update(
        {"crs": crs, "transform": transform, "width": width, "height": height}
    )

    memfile = MemoryFile()
    with memfile.open(**kwargs) as mem:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(mem, i),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=crs,
                resampling=Resampling.nearest,
            )

    # 2) Convert image to COG
    # Format creation option (see gdalwarp `-co` option)
    output_profile = cog_profiles.get("deflate")
    output_profile.update(dict(BIGTIFF="IF_SAFER"))

    # Dataset Open option (see gdalwarp `-oo` option)
    config = dict(
        GDAL_NUM_THREADS="ALL_CPUS",
        GDAL_TIFF_INTERNAL_MASK=True,
        GDAL_TIFF_OVR_BLOCKSIZE="128",
    )

    cog_filename = "/tmp/current_work_file.cog.tif"
    with memfile.open() as src_mem:
        cog_translate(
            src_mem,
            cog_filename,
            output_profile,
            config=config,
            in_memory=True,
            quiet=True,
            use_cog_driver=True,
            # web_optimized=True, # TODO: understand why this param hardcode epsg:3857 into the resulting file
            **options,
        )

    # 3) Lookup where to save the new COG file
    # Not doing any check, they where already done in validate_data_and_download()
    src_filename = fileset.file_set.first().uri
    dst_path = (
        get_object_key(get_base_dir(src_filename))
        + "/"
        + get_main_filename(src_filename)
        + ".cog.tif"
    )
    uri_protocol = src_filename.split("://")[0]
    if uri_protocol == "s3":
        Bucket = S3Bucket
        upload_file = s3_api.upload_file

    bucket = Bucket.objects.get(name=get_bucket_name(src_filename))
    upload_file(bucket=bucket, object_key=dst_path, src_path=cog_filename)
    fileset.refresh_from_db()
    fileset.visualization_uri = f"{uri_protocol}://{bucket.name}/{dst_path}"
    fileset.save()


def validate_data_and_download(fileset: Fileset) -> str:
    # check if content is present
    if fileset.file_set.count() != 1:
        # no content -> invalid
        # shapefile, multiple file content -> invalid (FIXME)
        fileset.set_invalid("wrong number of file")
        return None
    file = fileset.file_set.first()

    uri_protocol = file.uri.split("://")[0]
    if uri_protocol == "s3":
        Bucket = S3Bucket
        download_file = s3_api.download_file
    else:
        fileset.set_invalid("wrong uri")
        return None

    try:
        bucket = Bucket.objects.get(name=get_bucket_name(file.uri))
    except Bucket.DoesNotExist:
        fileset.set_invalid("bucket not found")
        return None

    # erase always the same file, make sure we don't consume too much ram
    local_name = "/tmp/current_work_file"

    download_file(bucket=bucket, object_key=get_object_key(file.uri), target=local_name)

    # is there data inside?
    if os.stat(local_name).st_size == 0:
        fileset.set_invalid("empty file")
        return None

    return local_name


def process_fileset(fileset: Fileset):
    filename = validate_data_and_download(fileset)
    if not filename:
        # previous error, abort processing
        logger.error(
            "fileset %s : %s",
            fileset.id,
            fileset.metadata["validation_error"],
        )
        return

    # raster, vector validation
    if fileset.role.format == FilesetFormat.VECTOR:
        content = validate_geopkg(fileset, filename)

    elif fileset.role.format == FilesetFormat.RASTER:
        content = validate_raster(fileset, filename)

    else:
        # tabular or other, so no validation rule for now -> return
        fileset.status = FilesetStatus.VALID
        fileset.save()
        return

    if content is None:
        fileset.refresh_from_db()
        if fileset.status != FilesetStatus.INVALID:
            # BUG! should be invalided by validate_raster or gpkg
            logger.error(
                "incoherence between content None and FilesetStatus (%s)",
                fileset.status,
            )
            fileset.status = FilesetStatus.INVALID
            fileset.save()
        return

    # TODO: should we validate the mime type?

    fileset_role_validator = {
        FilesetRoleCode.DEM: validate_dem,
        FilesetRoleCode.TRANSPORT_NETWORK: validate_transport,
        FilesetRoleCode.WATER: validate_water,
        FilesetRoleCode.LAND_COVER: validate_land_cover,
        FilesetRoleCode.HEALTH_FACILITIES: validate_facilities,
        FilesetRoleCode.TRAVEL_TIMES: validate_positive_raster,
        FilesetRoleCode.POPULATION: validate_positive_raster,
        FilesetRoleCode.STACK: validate_stack,
    }
    if fileset.role.code in fileset_role_validator:
        # custom validation by role
        fileset_role_validator[fileset.role.code](fileset, content)

    # end of validation -> not valid
    if fileset.status == FilesetStatus.INVALID:
        return

    # end of validation -> it's valid
    fileset.status = FilesetStatus.VALID
    fileset.save()

    # generate viz stuff
    if fileset.role.format == FilesetFormat.VECTOR:
        generate_geojson(fileset, filename)

    if fileset.role.format == FilesetFormat.RASTER:
        generate_cog_raster(fileset, filename)


def get_all_fileset_fields():
    for analysis_model in Analysis.get_analysis_models():
        for field in analysis_model._meta.get_fields():
            if isinstance(field, models.ForeignKey) and field.related_model == Fileset:
                yield (analysis_model, field.name)


def refresh_all_analysis(fileset: Fileset):
    for analysis_model, field_name in get_all_fileset_fields():
        for analysis in analysis_model.objects.filter(
            status=AnalysisStatus.DRAFT, **{field_name: fileset}
        ):
            try:
                analysis.update_status_if_draft()
            except Exception:
                logger.exception("refresh draft analysis post data validation")


def validate_fileset_job(queue, job) -> None:
    if missing_dependencies:
        logger.error("Validation deactivated, missing dependencies")
        return

    try:
        fileset = Fileset.objects.get(id=job.args["fileset_id"])

    except Fileset.DoesNotExist:
        logger.error("fileset %s not found", job.args["fileset_id"])
        return

    # quick exit to force stop processing
    if fileset.status != FilesetStatus.PENDING:
        logger.info(
            "Ignore validation fileset %s, already done", job.args["fileset_id"]
        )
        return

    # start processing
    logger.info("Starting validation fileset %s", job.args["fileset_id"])
    fileset.status = FilesetStatus.VALIDATING
    fileset.save()

    process_fileset(fileset)

    # refresh all related analysis, if any
    refresh_all_analysis(fileset)
    logger.info("Completed validation fileset %s", job.args["fileset_id"])


def validate_fileset_job_wrapped(*args, **kwargs) -> None:
    try:
        return validate_fileset_job(*args, **kwargs)
    except Exception:
        logger.exception("validate_fileset_job failed")


class ValidateFilesetQueue(AtMostOnceQueue):
    # override the default job model; our job model has a specific table name
    job_model = ValidateFilesetJob


# task queue for the connector_accessmod
# AtLeastOnceQueue + try/except: if the worker fail, restart the task. if the task fail, drop it + log
validate_fileset_queue = ValidateFilesetQueue(
    tasks={
        "validate_fileset": validate_fileset_job_wrapped,
    },
    notify_channel="validate_fileset_queue",
)
