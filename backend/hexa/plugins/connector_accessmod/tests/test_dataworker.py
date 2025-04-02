import os

import boto3
import rasterio
from django.test import override_settings
from moto import mock_aws
from rasterio import DatasetReader

from hexa.core.test import TestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    AnalysisStatus,
    File,
    Fileset,
    FilesetRole,
    FilesetRoleCode,
    FilesetStatus,
    Project,
)
from hexa.plugins.connector_accessmod.queue import validate_fileset_job
from hexa.plugins.connector_s3.models import Bucket
from hexa.plugins.connector_s3.tests.mocks.s3_credentials_mock import get_s3_mocked_env
from hexa.user_management.models import User


class MockJob:
    def __init__(self, args):
        self.args = args


@override_settings(**get_s3_mocked_env())
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
        cls.DEM_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.DEM,
        )
        cls.HEALTH_FACILITIES_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.HEALTH_FACILITIES,
        )
        cls.WATER_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.WATER,
        )
        cls.TRANSPORT_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.TRANSPORT_NETWORK,
        )
        cls.LAND_COVER_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.LAND_COVER,
        )
        cls.STACK_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.STACK,
        )
        cls.TRAVEL_TIMES_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.TRAVEL_TIMES,
        )
        cls.POPULATION_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.POPULATION,
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
            uri="s3://test-bucket/analysis/dem.tif",
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
            uri="s3://test-bucket/analysis/clinics.gpkg",
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
            uri="s3://test-bucket/analysis/water.gpkg",
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
            uri="s3://test-bucket/analysis/transport.gpkg",
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
            uri="s3://test-bucket/analysis/landcover.tif",
            fileset=cls.landcover_fs,
        )
        cls.stack_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="stack",
            status=FilesetStatus.PENDING,
            role=cls.STACK_ROLE,
            author=cls.AUTHOR,
        )
        cls.stack_file = File.objects.create(
            mime_type="image/geotiff",
            uri="s3://test-bucket/analysis/stack.tif",
            fileset=cls.stack_fs,
        )
        cls.travel_times_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="travel times",
            status=FilesetStatus.PENDING,
            role=cls.TRAVEL_TIMES_ROLE,
            author=cls.AUTHOR,
        )
        cls.travel_times_file = File.objects.create(
            mime_type="image/geotiff",
            uri="s3://test-bucket/analysis/travel_times.tif",
            fileset=cls.travel_times_fs,
        )
        cls.population_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="population",
            status=FilesetStatus.PENDING,
            role=cls.POPULATION_ROLE,
            author=cls.AUTHOR,
        )
        cls.population_file = File.objects.create(
            mime_type="image/geotiff",
            uri="s3://test-bucket/analysis/population.tif",
            fileset=cls.population_fs,
        )

        # S3 setup
        cls.BUCKET = Bucket.objects.create(name="test-bucket")

    @mock_aws
    def test_validate_no_file(self):
        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.dem_empty_fs.id)})
        )
        self.dem_empty_fs.refresh_from_db()
        self.assertEqual(self.dem_empty_fs.status, FilesetStatus.INVALID)

    @mock_aws
    def test_validate_dem(self):
        dem_file = os.path.dirname(__file__) + "/data/dem.tif"
        dem_data = open(dem_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="analysis/dem.tif", Body=dem_data
        )

        validate_fileset_job(None, MockJob(args={"fileset_id": str(self.dem_fs.id)}))
        self.dem_fs.refresh_from_db()
        self.assertEqual(
            self.dem_fs.metadata,
            {
                "1p": 188.0,
                "2p": 203.0,
                "98p": 445.0,
                "99p": 498.0,
                "max": 691,
                "min": 143,
                "nodata": 32767.0,
            },
        )
        self.assertEqual(
            self.dem_fs.visualization_uri, "s3://test-bucket/analysis/dem.cog.tif"
        )
        self.assertEqual(self.dem_fs.status, FilesetStatus.VALID)

    @mock_aws
    def test_validate_dem_wrong(self):
        dem_file = os.path.dirname(__file__) + "/data/dem_invalid.tif"
        dem_data = open(dem_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="analysis/dem.tif", Body=dem_data
        )

        validate_fileset_job(None, MockJob(args={"fileset_id": str(self.dem_fs.id)}))
        self.dem_fs.refresh_from_db()
        self.assertEqual(
            self.dem_fs.metadata,
            {"validation_error": "file content outside of reality"},
        )
        self.assertEqual(self.dem_fs.status, FilesetStatus.INVALID)

    @mock_aws
    def test_validate_facilities(self):
        facilities_file = os.path.dirname(__file__) + "/data/facilities.gpkg"
        facilities_data = open(facilities_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="analysis/clinics.gpkg", Body=facilities_data
        )

        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.facilities_fs.id)})
        )
        self.facilities_fs.refresh_from_db()
        self.assertEqual(self.facilities_fs.metadata, {"length": 3})
        self.assertEqual(
            self.facilities_fs.visualization_uri,
            "s3://test-bucket/analysis/clinics_viz.geojson",
        )
        self.assertEqual(self.facilities_fs.status, FilesetStatus.VALID)

    @mock_aws
    def test_validate_water(self):
        water_file = os.path.dirname(__file__) + "/data/water.gpkg"
        water_data = open(water_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="analysis/water.gpkg", Body=water_data
        )

        validate_fileset_job(None, MockJob(args={"fileset_id": str(self.water_fs.id)}))
        self.water_fs.refresh_from_db()
        self.assertEqual(
            self.water_fs.visualization_uri,
            "s3://test-bucket/analysis/water_viz.geojson",
        )
        self.assertEqual(self.water_fs.metadata, {"length": 3})
        self.assertEqual(self.water_fs.status, FilesetStatus.VALID)

    @mock_aws
    def test_validate_transport(self):
        transport_file = os.path.dirname(__file__) + "/data/transport.gpkg"
        transport_data = open(transport_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="analysis/transport.gpkg", Body=transport_data
        )

        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.transport_fs.id)})
        )
        self.transport_fs.refresh_from_db()
        self.assertEqual(
            self.transport_fs.metadata,
            {
                "columns": ["highway", "smoothness", "surface", "tracktype"],
                "values": {
                    "highway": ["primary", "secondary", "trunk_link"],
                    "smoothness": [],
                    "surface": ["asphalt"],
                    "tracktype": [],
                },
                "length": 3,
            },
        )
        self.assertEqual(
            self.transport_fs.visualization_uri,
            "s3://test-bucket/analysis/transport_viz.geojson",
        )
        self.assertEqual(self.transport_fs.status, FilesetStatus.VALID)

    @mock_aws
    def test_validate_landcover(self):
        landcover_file = os.path.dirname(__file__) + "/data/landcover.tif"
        landcover_data = open(landcover_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="analysis/landcover.tif", Body=landcover_data
        )

        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.landcover_fs.id)})
        )
        self.landcover_fs.refresh_from_db()
        self.assertEqual(
            self.landcover_fs.metadata,
            {
                "unique_values": [0, 1, 2, 3, 4, 6, 7, 8, 10],
                "nodata": 0.0,
            },
        )
        self.assertEqual(
            self.landcover_fs.visualization_uri,
            "s3://test-bucket/analysis/landcover.cog.tif",
        )
        self.assertEqual(self.landcover_fs.status, FilesetStatus.VALID)

    @mock_aws
    def test_validate_stack(self):
        stack_file = os.path.dirname(__file__) + "/data/stack.tif"
        stack_data = open(stack_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="analysis/stack.tif", Body=stack_data
        )

        validate_fileset_job(None, MockJob(args={"fileset_id": str(self.stack_fs.id)}))
        self.stack_fs.refresh_from_db()
        self.assertEqual(
            self.stack_fs.metadata,
            {
                "unique_values": [0, 1, 2, 3, 4, 6, 7, 8, 10],
                "nodata": 0.0,
            },
        )
        self.assertEqual(
            self.stack_fs.visualization_uri,
            "s3://test-bucket/analysis/stack.cog.tif",
        )
        self.assertEqual(self.stack_fs.status, FilesetStatus.VALID)

    @mock_aws
    def test_validate_travel_times(self):
        travel_times_file = os.path.dirname(__file__) + "/data/travel.tif"
        travel_times_data = open(travel_times_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket",
            Key="analysis/travel_times.tif",
            Body=travel_times_data,
        )

        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.travel_times_fs.id)})
        )
        self.travel_times_fs.refresh_from_db()
        self.assertEqual(
            self.travel_times_fs.metadata,
            {
                "1p": 188.0,
                "2p": 203.0,
                "98p": 445.0,
                "99p": 498.0,
                "max": 691,
                "min": 143,
                "nodata": 32767.0,
            },
        )
        self.assertEqual(
            self.travel_times_fs.visualization_uri,
            "s3://test-bucket/analysis/travel_times.cog.tif",
        )
        self.assertEqual(self.travel_times_fs.status, FilesetStatus.VALID)

    @mock_aws
    def test_validate_population(self):
        population_file = os.path.dirname(__file__) + "/data/population.tif"
        population_data = open(population_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket",
            Key="analysis/population.tif",
            Body=population_data,
        )

        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.population_fs.id)})
        )
        self.population_fs.refresh_from_db()
        self.assertEqual(
            self.population_fs.metadata,
            {
                "1p": 188.0,
                "2p": 203.0,
                "98p": 445.0,
                "99p": 498.0,
                "max": 691,
                "min": 143,
                "nodata": 32767.0,
            },
        )
        self.assertEqual(
            self.population_fs.visualization_uri,
            "s3://test-bucket/analysis/population.cog.tif",
        )
        self.assertEqual(self.population_fs.status, FilesetStatus.VALID)


@override_settings(**get_s3_mocked_env())
class AccessmodAnalysisUpdateTest(TestCase):
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
        cls.DEM_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.DEM,
        )
        cls.HEALTH_FACILITIES_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.HEALTH_FACILITIES,
        )
        cls.TRANSPORT_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.TRANSPORT_NETWORK,
        )
        cls.LAND_COVER_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.LAND_COVER,
        )
        cls.dem_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="dem",
            status=FilesetStatus.TO_ACQUIRE,
            role=cls.DEM_ROLE,
            author=cls.AUTHOR,
        )
        cls.facilities_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="facilities",
            status=FilesetStatus.TO_ACQUIRE,
            role=cls.HEALTH_FACILITIES_ROLE,
            author=cls.AUTHOR,
        )
        cls.transport_fs = Fileset.objects.create(
            project=cls.PROJECT,
            name="transport",
            status=FilesetStatus.TO_ACQUIRE,
            role=cls.TRANSPORT_ROLE,
            author=cls.AUTHOR,
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
            uri="s3://test-bucket/analysis/landcover.tif",
            fileset=cls.landcover_fs,
        )

        # S3 setup
        cls.BUCKET = Bucket.objects.create(name="test-bucket")

        # an analysis
        cls.waiting_analysis = AccessibilityAnalysis.objects.create(
            project=cls.PROJECT,
            status=AnalysisStatus.DRAFT,
            name="a name",
            land_cover=cls.landcover_fs,
            dem=cls.dem_fs,
            transport_network=cls.transport_fs,
            health_facilities=cls.facilities_fs,
            stack_priorities=[1, 2],
        )

    @mock_aws
    def test_update_analysis_status(self):
        landcover_file = os.path.dirname(__file__) + "/data/landcover.tif"
        landcover_data = open(landcover_file, "rb").read()
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="test-bucket")
        s3_client.put_object(
            Bucket="test-bucket", Key="analysis/landcover.tif", Body=landcover_data
        )
        validate_fileset_job(
            None, MockJob(args={"fileset_id": str(self.landcover_fs.id)})
        )
        self.landcover_fs.refresh_from_db()
        self.assertEqual(self.landcover_fs.status, FilesetStatus.VALID)
        self.waiting_analysis.refresh_from_db()
        self.assertEqual(self.waiting_analysis.status, AnalysisStatus.READY)

    def test_cog(self):
        """Reading Geotiffs can be a tricky business - sometimes, updating deps such as rio-cogeo or rasterio
        will break compression support
        """
        cog_path = os.path.dirname(__file__) + "/data/cumulative_cost.tif"
        cog = rasterio.open(cog_path)
        self.assertIsInstance(cog, DatasetReader)
