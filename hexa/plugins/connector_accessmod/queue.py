import os
import typing
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
from dpq.queue import AtLeastOnceQueue

import hexa.plugins.connector_s3.api as s3_api
from hexa.plugins.connector_s3.models import Bucket

from .models import (
    Analysis,
    AnalysisStatus,
    Fileset,
    FilesetRoleCode,
    FilesetStatus,
    ValidateFilesetJob,
)

logger = getLogger(__name__)


def get_bucket_name(uri: str) -> str:
    # extract bucketname, assume a s3://path/file URI
    bucket_name, *key_parts = uri[5:].split("/")
    return bucket_name


def get_object_key(uri: str) -> str:
    # extract object key, assume a s3://path/file URI
    bucket_name, *key_parts = uri[5:].split("/")
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

    if fileset.status == FilesetStatus.INVALID:
        # invalid by previous checks
        return

    # end of processing -> validated
    fileset.status = FilesetStatus.VALID
    fileset.save()
    
    generate_geojson(fileset, filename)


def validate_water(fileset: Fileset, filename: str):
    water = gpd.read_file(filename)
    validate_geopkg(water, fileset, ("LineString", "MultiLineString", "MultiPolygon"))

    if fileset.status == FilesetStatus.INVALID:
        # invalid by previous checks
        return

    # end of processing -> validated
    fileset.status = FilesetStatus.VALID
    fileset.save()
    
    generate_geojson(fileset, filename)


def validate_transport(fileset: Fileset, filename: str):
    transport = gpd.read_file(filename)
    validate_geopkg(transport, fileset, ("LineString", "MultiLineString"))

    if fileset.status == FilesetStatus.INVALID:
        # invalid by previous checks
        return

    # extract roads categories & validate
    if fileset.metadata is None:
        fileset.metadata = {}

    cols = sorted(transport.columns.to_list())
    cols.remove("geometry")
    fileset.metadata["columns"] = cols
    fileset.metadata["values"] = {}
    for col in cols:
        # save some unique values for all columns, front can choose what it wants
        # truncate to max 20 elements
        # FIXME: will fail for weird python scalar like datetime, timedelta etc
        # which are not json encodable
        values = transport.get(col).unique()[:20].tolist()
        fileset.metadata["values"][col] = sorted(
            filter(lambda v: not pd.isna(v), values)
        )

    fileset.status = FilesetStatus.VALID
    fileset.save()
    
    generate_geojson(fileset, filename)


def generate_geojson(fileset: Fileset, filename: str, **options):
    # Generate a GeoJSON copy from a fileset. change CRS if needed
    # used by frontend

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
    bucket = Bucket.objects.get(name=get_bucket_name(src_filename))
    s3_api.upload_file(bucket=bucket, object_key=dst_path, src_path=json_filename)
    fileset.metadata["geojson_uri"] = f"s3://{bucket.name}/{dst_path}"
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
    # assume s3 bucket
    src_filename = fileset.file_set.first().uri
    dst_path = (
        get_object_key(get_base_dir(src_filename))
        + "/"
        + get_main_filename(src_filename)
        + ".cog.tif"
    )
    bucket = Bucket.objects.get(name=get_bucket_name(src_filename))
    s3_api.upload_file(bucket=bucket, object_key=dst_path, src_path=cog_filename)
    fileset.metadata["cog_raster_uri"] = f"s3://{bucket.name}/{dst_path}"
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

    if fileset.metadata is None:
        fileset.metadata = {}

    fileset.metadata["min"] = int(dem_content.min())
    fileset.metadata["max"] = int(dem_content.max())
    if dem.nodata is None:
        fileset.metadata["nodata"] = None
    else:
        fileset.metadata["nodata"] = int(dem.nodata)

    percentile = np.percentile(a=dem_content.compressed(), q=[1, 2, 98, 99])
    fileset.metadata["1p"] = float(percentile[0])
    fileset.metadata["2p"] = float(percentile[1])
    fileset.metadata["98p"] = float(percentile[2])
    fileset.metadata["99p"] = float(percentile[3])

    fileset.status = FilesetStatus.VALID
    fileset.save()

    generate_cog_raster(fileset, filename)


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
    fileset.metadata["unique_values"] = sorted([int(i) for i in lc_classes])
    if landcover.nodata is None:
        fileset.metadata["nodata"] = None
    else:
        fileset.metadata["nodata"] = landcover.nodata
    fileset.status = FilesetStatus.VALID
    fileset.save()

    generate_cog_raster(fileset, filename)


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

    try:
        bucket = Bucket.objects.get(name=get_bucket_name(file.uri))
    except Bucket.DoesNotExist:
        fileset.set_invalid("bucket not found")
        return None

    # erase always the same file, make sure we don't consume too much ram
    local_name = "/tmp/current_work_file"
    s3_api.download_file(
        bucket=bucket, object_key=get_object_key(file.uri), target=local_name
    )

    # is there data inside?
    if os.stat(local_name).st_size == 0:
        fileset.set_invalid("empty file")
        return None

    return local_name


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

    # refresh all related analysis, if any
    refresh_all_analysis(fileset)
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
