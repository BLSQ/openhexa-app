import os

import boto3
from django.test import tag
from moto import mock_s3, mock_sts

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    File,
    Fileset,
    FilesetFormat,
    FilesetRole,
    FilesetRoleCode,
    FilesetStatus,
    Project,
)
from hexa.plugins.connector_accessmod.queue import validate_fileset_job
from hexa.plugins.connector_s3.models import Bucket, Credentials
from hexa.user_management.models import User


class MockJob(object):
    def __init__(self, args):
        self.args = args


class AccessmodDataWorkerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.AUTHOR = User.objects.create_user(
            "author@bluesquarehub.com",
            "lolpassword",
            is_superuser=True,
        )

        # AM setup
        cls.PROJECT = Project.objects.create(
            name="Container",
            country="BFA",
            author=cls.AUTHOR,
            spatial_resolution=1000,
            crs=6933,
        )
        cls.DEM_ROLE = FilesetRole.objects.create(
            name="DEM",
            code=FilesetRoleCode.DEM,
            format=FilesetFormat.RASTER,
        )
        cls.HEALTH_FACILITIES_ROLE = FilesetRole.objects.create(
            name="HEALTH_FACILITIES",
            code=FilesetRoleCode.HEALTH_FACILITIES,
            format=FilesetFormat.VECTOR,
        )
        cls.WATER_ROLE = FilesetRole.objects.create(
            name="WATER",
            code=FilesetRoleCode.WATER,
            format=FilesetFormat.VECTOR,
        )
        cls.TRANSPORT_ROLE = FilesetRole.objects.create(
            name="TRANSPORT",
            code=FilesetRoleCode.TRANSPORT_NETWORK,
            format=FilesetFormat.VECTOR,
        )
        cls.LAND_COVER_ROLE = FilesetRole.objects.create(
            name="LAND_COVER",
            code=FilesetRoleCode.LAND_COVER,
            format=FilesetFormat.VECTOR,
        )
        cls.dem_empty_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="empty dem",
            status=FilesetStatus.PENDING,
            role=cls.DEM_ROLE,
            author=cls.AUTHOR,
        )
        cls.dem_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="dem",
            status=FilesetStatus.PENDING,
            role=cls.DEM_ROLE,
            author=cls.AUTHOR,
        )
        cls.dem_file = File.objects.create(
            mime_type="image/geotiff",
            uri="s3://test-bucket/dem.tif",
            fileset=cls.dem_fs,
        )
        cls.facilities_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="facilities",
            status=FilesetStatus.PENDING,
            role=cls.HEALTH_FACILITIES_ROLE,
            author=cls.AUTHOR,
        )
        cls.facilities_file = File.objects.create(
            mime_type="application/geopackage+sqlite3",
            uri="s3://test-bucket/clinics.gpkg",
            fileset=cls.facilities_fs,
        )
        cls.water_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="water",
            status=FilesetStatus.PENDING,
            role=cls.WATER_ROLE,
            author=cls.AUTHOR,
        )
        cls.water_file = File.objects.create(
            mime_type="application/geopackage+sqlite3",
            uri="s3://test-bucket/water.gpkg",
            fileset=cls.water_fs,
        )
        cls.transport_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="transport",
            status=FilesetStatus.PENDING,
            role=cls.TRANSPORT_ROLE,
            author=cls.AUTHOR,
        )
        cls.transport_file = File.objects.create(
            mime_type="application/geopackage+sqlite3",
            uri="s3://test-bucket/transport.gpkg",
            fileset=cls.transport_fs,
        )
        cls.landcover_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="landcover",
            status=FilesetStatus.PENDING,
            role=cls.LAND_COVER_ROLE,
            author=cls.AUTHOR,
        )
        cls.landcover_file = File.objects.create(
            mime_type="image/geotiff",
            uri="s3://test-bucket/landcover.tif",
            fileset=cls.landcover_fs,
        )

        # S3 setup
        cls.CREDENTIALS = Credentials.objects.create(
            username="test-username",
            default_region="us-east-1",
            user_arn="test-user-arn-arn-arn",
            app_role_arn="test-app-arn-arn-arn",
        )
        cls.BUCKET = Bucket.objects.create(name="test-bucket")

    @mock_s3
    @mock_sts
    @tag("datasciences")
    def test_validate_no_file(self):
        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.dem_empty_fs.id)})
        )
        self.dem_empty_fs.refresh_from_db()
        self.assertEqual(self.dem_empty_fs.status, FilesetStatus.INVALID)

    @mock_s3
    @mock_sts
    @tag("datasciences")
    def test_validate_dem(self):
        dem_file = os.path.dirname(__file__) + "/data/dem.tif"
        dem_data = open(dem_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(Bucket="test-bucket", Key="dem.tif", Body=dem_data)

        validate_fileset_job(None, MockJob(args={"fileset_id": str(self.dem_fs.id)}))
        self.dem_fs.refresh_from_db()
        self.assertEqual(self.dem_fs.metadata, {})
        self.assertEqual(self.dem_fs.status, FilesetStatus.VALID)

    @mock_s3
    @mock_sts
    @tag("datasciences")
    def test_validate_facilities(self):
        facilities_file = os.path.dirname(__file__) + "/data/facilities.gpkg"
        facilities_data = open(facilities_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="clinics.gpkg", Body=facilities_data
        )

        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.facilities_fs.id)})
        )
        self.facilities_fs.refresh_from_db()
        self.assertEqual(self.facilities_fs.metadata, {})
        self.assertEqual(self.facilities_fs.status, FilesetStatus.VALID)

    @mock_s3
    @mock_sts
    @tag("datasciences")
    def test_validate_water(self):
        water_file = os.path.dirname(__file__) + "/data/water.gpkg"
        water_data = open(water_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(Bucket="test-bucket", Key="water.gpkg", Body=water_data)

        validate_fileset_job(None, MockJob(args={"fileset_id": str(self.water_fs.id)}))
        self.water_fs.refresh_from_db()
        self.assertEqual(self.water_fs.metadata, {})
        self.assertEqual(self.water_fs.status, FilesetStatus.VALID)

    @mock_s3
    @mock_sts
    @tag("datasciences")
    def test_validate_transport(self):
        transport_file = os.path.dirname(__file__) + "/data/transport.gpkg"
        transport_data = open(transport_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="transport.gpkg", Body=transport_data
        )

        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.transport_fs.id)})
        )
        self.transport_fs.refresh_from_db()
        self.assertEqual(
            self.transport_fs.metadata,
            {"highways": ["primary", "secondary", "trunk_link"]},
        )
        self.assertEqual(self.transport_fs.status, FilesetStatus.VALID)

    @mock_s3
    @mock_sts
    @tag("datasciences")
    def test_validate_landcover(self):
        landcover_file = os.path.dirname(__file__) + "/data/landcover.tif"
        landcover_data = open(landcover_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="landcover.tif", Body=landcover_data
        )

        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.landcover_fs.id)})
        )
        self.landcover_fs.refresh_from_db()
        self.assertEqual(
            self.landcover_fs.metadata, {"classes": [0, 1, 2, 3, 4, 6, 7, 8, 10]}
        )
        self.assertEqual(self.landcover_fs.status, FilesetStatus.VALID)
