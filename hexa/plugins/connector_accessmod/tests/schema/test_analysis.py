import uuid
from unittest.mock import patch
from urllib.parse import urljoin

import responses
from django.conf import settings
from django.core.signing import Signer
from django.utils.dateparse import parse_datetime

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    AccessibilityAnalysisAlgorithm,
    AnalysisStatus,
    Fileset,
    FilesetRole,
    FilesetRoleCode,
    FilesetStatus,
    GeographicCoverageAnalysis,
    Project,
    ProjectPermission,
    ZonalStatisticsAnalysis,
)
from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGRunState, DAGTemplate
from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import PermissionMode, User


class AnalysisTest(GraphQLTestCase):
    CLUSTER = None
    USER_1 = None
    DAG_ACCESSIBILITY_TEMPLATE = None
    DAG_COVERAGE_TEMPLATE = None
    DAG_ACCESSIBILITY = None
    DAG_COVERAGE = None
    DEM_ROLE = None
    FRICTION_SURFACE_ROLE = None
    GEOMETRY_ROLE = None
    HEALTH_FACILITIES_ROLE = None
    LAND_COVER_ROLE = None
    POPULATION_ROLE = None
    STACK_ROLE = None
    TRANSPORT_NETWORK_ROLE = None
    WATER_ROLE = None
    BOUNDARIES_ROLE = None
    TRAVEL_TIMES_ROLE = None
    DEM_FILESET = None
    FRICTION_SURFACE_FILESET = None
    HEALTH_FACILITIES_FILESET = None
    LAND_COVER_FILESET = None
    TRANSPORT_NETWORK_FILESET = None
    WATER_FILESET = None
    POPULATION_FILESET = None
    STACK_FILESET = None
    BOUNDARIES_FILESET = None
    TRAVEL_TIMES_FILESET = None
    SAMPLE_PROJECT = None

    @classmethod
    def setUpTestData(cls):
        cls.USER_1 = User.objects.create_user(
            "jim@bluesquarehub.com", "jimrocks", is_superuser=True
        )
        cls.USER_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks",
        )
        bucket_name = settings.ACCESSMOD_BUCKET_NAME.split("://")[1].rstrip("/")
        cls.BUCKET = Bucket.objects.create(name=bucket_name)
        cls.CLUSTER = Cluster.objects.create(
            name="test_cluster", url="https://lookimacluster.com/api"
        )
        cls.DAG_ACCESSIBILITY_TEMPLATE = DAGTemplate.objects.create(
            cluster=cls.CLUSTER,
            code="AM_ACCESSIBILITY",
            description="AccessMod accessibility analysis",
            sample_config={"foo": "bar"},
        )
        cls.DAG_ACCESSIBILITY = DAG.objects.create(
            template=cls.DAG_ACCESSIBILITY_TEMPLATE,
            dag_id="am_accessibility_full",
        )
        cls.DAG_COVERAGE_TEMPLATE = DAGTemplate.objects.create(
            cluster=cls.CLUSTER,
            code="AM_COVERAGE",
            description="AccessMod geographic coverage Analysis",
            sample_config={"bar": "baz"},
        )
        cls.DAG_COVERAGE = DAG.objects.create(
            template=cls.DAG_COVERAGE_TEMPLATE,
            dag_id="am_coverage",
        )

        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="BE",
            author=cls.USER_1,
            spatial_resolution=100,
            crs=4326,
        )
        ProjectPermission.objects.create(
            user=cls.USER_1, project=cls.SAMPLE_PROJECT, mode=PermissionMode.OWNER
        )
        cls.GEOMETRY_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.GEOMETRY,
        )
        cls.LAND_COVER_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.LAND_COVER,
        )
        cls.DEM_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.DEM,
        )
        cls.TRANSPORT_NETWORK_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.TRANSPORT_NETWORK,
        )
        cls.WATER_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.WATER,
        )
        cls.HEALTH_FACILITIES_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.HEALTH_FACILITIES,
        )
        cls.FRICTION_SURFACE_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.FRICTION_SURFACE,
        )
        cls.POPULATION_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.POPULATION,
        )
        cls.STACK_ROLE = FilesetRole.objects.get(code=FilesetRoleCode.STACK)
        cls.LAND_COVER_FILESET = Fileset.objects.create(
            name="An impressive land cover",
            role=cls.LAND_COVER_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
            status=FilesetStatus.VALID,
        )
        cls.DEM_FILESET = Fileset.objects.create(
            name="My favorite DEM",
            role=cls.DEM_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
            status=FilesetStatus.VALID,
        )
        cls.TRANSPORT_NETWORK_FILESET = Fileset.objects.create(
            name="Worst Transport Network ever",
            role=cls.TRANSPORT_NETWORK_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
            status=FilesetStatus.VALID,
        )
        cls.WATER_FILESET = Fileset.objects.create(
            name="I like water",
            role=cls.WATER_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
            status=FilesetStatus.VALID,
        )
        cls.HEALTH_FACILITIES_FILESET = Fileset.objects.create(
            name="Would you look at those health facilities!",
            role=cls.HEALTH_FACILITIES_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
            status=FilesetStatus.VALID,
        )
        cls.FRICTION_SURFACE_FILESET = Fileset.objects.create(
            name="Check this friction surface!",
            role=cls.FRICTION_SURFACE_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
        )
        cls.STACK_FILESET = Fileset.objects.create(
            name="Stack file",
            role=cls.STACK_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
            status=FilesetStatus.VALID,
        )
        cls.POPULATION_FILESET = Fileset.objects.create(
            name="Best population ever",
            role=cls.POPULATION_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
        )
        cls.ACCESSIBILITY_ANALYSIS_1 = AccessibilityAnalysis.objects.create(
            author=cls.USER_1,
            project=cls.SAMPLE_PROJECT,
            name="First accessibility analysis",
            dem=cls.DEM_FILESET,
            stack=cls.STACK_FILESET,
        )
        cls.ACCESSIBILITY_ANALYSIS_2 = AccessibilityAnalysis.objects.create(
            author=cls.USER_1,
            project=cls.SAMPLE_PROJECT,
            name="Second accessibility analysis",
            dem=cls.DEM_FILESET,
            health_facilities=cls.HEALTH_FACILITIES_FILESET,
            land_cover=cls.LAND_COVER_FILESET,
            transport_network=cls.TRANSPORT_NETWORK_FILESET,
            water=cls.WATER_FILESET,
            status=AnalysisStatus.READY,  # let's cheat a little
            stack=cls.STACK_FILESET,
            max_travel_time=42,
        )
        cls.GEOGRAPHIC_COVERAGE_ANALYSIS_1 = GeographicCoverageAnalysis.objects.create(
            author=cls.USER_1,
            project=cls.SAMPLE_PROJECT,
            name="First Geo coverage analysis",
            population=cls.POPULATION_FILESET,
            friction_surface=cls.FRICTION_SURFACE_FILESET,
            dem=cls.DEM_FILESET,
            health_facilities=cls.HEALTH_FACILITIES_FILESET,
            hf_processing_order="plop",
        )
        cls.GEOGRAPHIC_COVERAGE_ANALYSIS_2 = GeographicCoverageAnalysis.objects.create(
            author=cls.USER_1,
            status=AnalysisStatus.RUNNING,
            project=cls.SAMPLE_PROJECT,
            name="Second Geo coverage analysis",
            population=cls.POPULATION_FILESET,
            friction_surface=cls.FRICTION_SURFACE_FILESET,
            dem=cls.DEM_FILESET,
            health_facilities=cls.HEALTH_FACILITIES_FILESET,
            hf_processing_order="yolo",
        )
        cls.BOUNDARIES_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.BOUNDARIES,
        )
        cls.TRAVEL_TIMES_ROLE = FilesetRole.objects.get(
            code=FilesetRoleCode.TRAVEL_TIMES,
        )
        cls.BOUNDARIES_FILESET = Fileset.objects.create(
            name="A boundaries fileset",
            role=cls.BOUNDARIES_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
            status=FilesetStatus.VALID,
        )
        cls.TRAVEL_TIMES_FILESET = Fileset.objects.create(
            name="A traveltime fileset",
            role=cls.TRAVEL_TIMES_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
            status=FilesetStatus.VALID,
        )
        cls.ZONAL_STATISTICS_ANALYSIS_1 = ZonalStatisticsAnalysis.objects.create(
            author=cls.USER_1,
            project=cls.SAMPLE_PROJECT,
            name="First Zonal Statistics analysis",
            travel_times=cls.TRAVEL_TIMES_FILESET,
            boundaries=cls.BOUNDARIES_FILESET,
        )

    def test_accessmod_analysis_owner(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
              query accessmodAnalysis($id: String!) {
                accessmodAnalysis(id: $id) {
                  id
                  type
                  status
                  name
                  ...on AccessmodOwnership {
                    owner {
                        ... on User {
                        email
                        }
                    }
                  }
                  ... on AccessmodAccessibilityAnalysis {
                    landCover {
                      id
                    }
                    dem {
                      id
                    }
                    transportNetwork {
                      id
                    }
                    water {
                      id
                    }
                    barrier {
                      id
                    }
                    movingSpeeds
                    healthFacilities {
                      id
                    }
                    invertDirection
                    maxTravelTime
                    waterAllTouched
                    algorithm
                    knightMove
                    stack {
                        id
                    }
                    travelTimes {
                      id
                    }
                    frictionSurface {
                      id
                    }
                  }
                }
              }
            """,
            {"id": str(self.ACCESSIBILITY_ANALYSIS_1.id)},
        )

        self.assertEqual(
            {
                "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                "type": self.ACCESSIBILITY_ANALYSIS_1.type,
                "status": self.ACCESSIBILITY_ANALYSIS_1.status,
                "name": self.ACCESSIBILITY_ANALYSIS_1.name,
                "owner": {"email": self.USER_1.email},
                "stack": {"id": str(self.ACCESSIBILITY_ANALYSIS_1.stack.id)},
                "landCover": None,
                "dem": {"id": str(self.ACCESSIBILITY_ANALYSIS_1.dem.id)},
                "transportNetwork": None,
                "water": None,
                "barrier": None,
                "movingSpeeds": {},
                "healthFacilities": None,
                "invertDirection": False,
                "maxTravelTime": 360,
                "waterAllTouched": True,
                "algorithm": AccessibilityAnalysisAlgorithm.ISOTROPIC,
                "knightMove": False,
                "travelTimes": None,
                "frictionSurface": None,
            },
            r["data"]["accessmodAnalysis"],
        )

    def test_accessmod_analysis_not_owner(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodAnalysis($id: String!) {
                  accessmodAnalysis(id: $id) {
                    id
                  }
                }
            """,
            {"id": str(self.ACCESSIBILITY_ANALYSIS_1.id)},
        )

        self.assertEqual(
            r["data"]["accessmodAnalysis"],
            None,
        )

    def test_struct_accessmod_zonal_statistics_analysis(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
              query accessmodAnalysis($id: String!) {
                accessmodAnalysis(id: $id) {
                  id
                  type
                  status
                  name
                  ...on AccessmodOwnership {
                    owner {
                        ... on User {
                        email
                        }
                    }
                  }
                  ... on AccessmodZonalStatistics {
                    population {
                      id
                    }
                    travelTimes {
                      id
                    }
                    boundaries {
                      id
                    }
                    timeThresholds
                    zonalStatisticsTable {
                      id
                    }
                    zonalStatisticsGeo {
                      id
                    }
                  }
                }
              }
            """,
            {"id": str(self.ZONAL_STATISTICS_ANALYSIS_1.id)},
        )

        self.assertEqual(
            {
                "id": str(self.ZONAL_STATISTICS_ANALYSIS_1.id),
                "type": self.ZONAL_STATISTICS_ANALYSIS_1.type.value,
                "status": str(self.ZONAL_STATISTICS_ANALYSIS_1.status),
                "name": self.ZONAL_STATISTICS_ANALYSIS_1.name,
                "owner": {"email": self.USER_1.email},
                "population": None,
                "travelTimes": {"id": str(self.TRAVEL_TIMES_FILESET.id)},
                "boundaries": {"id": str(self.BOUNDARIES_FILESET.id)},
                "timeThresholds": [60, 120, 180, 240, 300, 360],
                "zonalStatisticsTable": None,
                "zonalStatisticsGeo": None,
            },
            r["data"]["accessmodAnalysis"],
        )

    def test_accessmod_analyses(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodAnalyses($projectId: String!) {
                    accessmodAnalyses(projectId: $projectId) {
                        pageNumber
                        totalPages
                        totalItems
                        items {
                            id
                            type
                            ... on AccessmodGeographicCoverageAnalysis {
                                frictionSurface {
                                    id
                                }
                            }
                        }
                    }
                }
            """,
            {"projectId": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessmodAnalyses"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 5,
                "items": [
                    {
                        "id": str(self.ZONAL_STATISTICS_ANALYSIS_1.id),
                        "type": self.ZONAL_STATISTICS_ANALYSIS_1.type.value,
                    },
                    {
                        "id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.id),
                        "type": self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.type.value,
                        "frictionSurface": {
                            "id": str(
                                self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.friction_surface.id
                            )
                        },
                    },
                    {
                        "id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS_1.id),
                        "type": self.GEOGRAPHIC_COVERAGE_ANALYSIS_1.type.value,
                        "frictionSurface": {
                            "id": str(
                                self.GEOGRAPHIC_COVERAGE_ANALYSIS_1.friction_surface.id
                            )
                        },
                    },
                    {
                        "id": str(self.ACCESSIBILITY_ANALYSIS_2.id),
                        "type": self.ACCESSIBILITY_ANALYSIS_2.type.value,
                    },
                    {
                        "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                        "type": self.ACCESSIBILITY_ANALYSIS_1.type.value,
                    },
                ],
            },
        )

    def test_accessmod_analyses_with_pagination(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodAnalyses($projectId: String!) {
                  accessmodAnalyses(projectId: $projectId, page: 1, perPage: 10) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
            {"projectId": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessmodAnalyses"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 5,
                "items": [
                    {"id": str(self.ZONAL_STATISTICS_ANALYSIS_1.id)},
                    {"id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.id)},
                    {"id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS_1.id)},
                    {"id": str(self.ACCESSIBILITY_ANALYSIS_2.id)},
                    {"id": str(self.ACCESSIBILITY_ANALYSIS_1.id)},
                ],
            },
        )

    def test_accessmod_analyses_empty(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodAnalyses($projectId: String!) {
                  accessmodAnalyses(projectId: $projectId) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
            {"projectId": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessmodAnalyses"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 0,
                "items": [],
            },
        )

    def test_accessmod_analyses_type_resolver(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodAnalyses($projectId: String!) {
                    accessmodAnalyses(projectId: $projectId) {
                        totalItems
                        items {
                            name
                        }
                    }
                }
            """,
            {"projectId": str(self.SAMPLE_PROJECT.id)},
        )

        self.assertEqual(
            r["data"]["accessmodAnalyses"],
            {
                "totalItems": 5,
                "items": [
                    {
                        "name": self.ZONAL_STATISTICS_ANALYSIS_1.name,
                    },
                    {
                        "name": self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.name,
                    },
                    {
                        "name": self.GEOGRAPHIC_COVERAGE_ANALYSIS_1.name,
                    },
                    {
                        "name": self.ACCESSIBILITY_ANALYSIS_2.name,
                    },
                    {
                        "name": self.ACCESSIBILITY_ANALYSIS_1.name,
                    },
                ],
            },
        )

    def test_create_accessmod_accessibility_analysis(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation createAccessmodAccessibilityAnalysis($input: CreateAccessmodAccessibilityAnalysisInput) {
                  createAccessmodAccessibilityAnalysis(input: $input) {
                    success
                    analysis {
                        id
                        name
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "name": "A new accessibility analysis",
                }
            },
        )

        self.assertEqual(
            r["data"]["createAccessmodAccessibilityAnalysis"]["success"], True
        )
        self.assertEqual(
            r["data"]["createAccessmodAccessibilityAnalysis"]["analysis"]["name"],
            "A new accessibility analysis",
        )
        self.assertIsInstance(
            r["data"]["createAccessmodAccessibilityAnalysis"]["analysis"]["name"], str
        )
        self.assertEqual(
            [], r["data"]["createAccessmodAccessibilityAnalysis"]["errors"]
        )

    def test_create_accessmod_accessibility_analysis_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation createAccessmodAccessibilityAnalysis($input: CreateAccessmodAccessibilityAnalysisInput) {
                  createAccessmodAccessibilityAnalysis(input: $input) {
                    success
                    analysis {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "name": self.ACCESSIBILITY_ANALYSIS_2.name,
                }
            },
        )

        self.assertEqual(
            {"success": False, "analysis": None, "errors": ["NAME_DUPLICATE"]},
            r["data"]["createAccessmodAccessibilityAnalysis"],
        )

    def test_update_accessmod_accessibility_analysis(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation updateAccessmodAccessibilityAnalysis($input: UpdateAccessmodAccessibilityAnalysisInput) {
                  updateAccessmodAccessibilityAnalysis(input: $input) {
                    success
                    analysis {
                        id
                        name
                        status
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                    "name": "Updated accessibility analysis!",
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "analysis": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                    "name": "Updated accessibility analysis!",
                    "status": AnalysisStatus.DRAFT,
                },
                "errors": [],
            },
            r["data"]["updateAccessmodAccessibilityAnalysis"],
        )

        r = self.run_query(
            """
                mutation updateAccessmodAccessibilityAnalysis($input: UpdateAccessmodAccessibilityAnalysisInput) {
                  updateAccessmodAccessibilityAnalysis(input: $input) {
                    success
                    analysis {
                        status
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                    "name": "Updated accessibility analysis!",
                    "landCoverId": str(self.LAND_COVER_FILESET.id),
                    "demId": str(self.DEM_FILESET.id),
                    "transportNetworkId": str(self.TRANSPORT_NETWORK_FILESET.id),
                    "waterId": str(self.WATER_FILESET.id),
                    "stackId": str(self.STACK_FILESET.id),
                    "stackPriorities": [],
                    "healthFacilitiesId": str(self.HEALTH_FACILITIES_FILESET.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "analysis": {"status": AnalysisStatus.READY},
                "errors": [],
            },
            r["data"]["updateAccessmodAccessibilityAnalysis"],
        )

    def test_update_accessmod_accessibility_analysis_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation updateAccessmodAccessibilityAnalysis($input: UpdateAccessmodAccessibilityAnalysisInput) {
                  updateAccessmodAccessibilityAnalysis(input: $input) {
                    success
                    analysis {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                    "name": self.ACCESSIBILITY_ANALYSIS_2.name,
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "analysis": {"id": str(self.ACCESSIBILITY_ANALYSIS_1.id)},
                "errors": ["NAME_DUPLICATE"],
            },
            r["data"]["updateAccessmodAccessibilityAnalysis"],
        )

        r = self.run_query(
            """
                mutation updateAccessmodAccessibilityAnalysis($input: UpdateAccessmodAccessibilityAnalysisInput) {
                  updateAccessmodAccessibilityAnalysis(input: $input) {
                    success
                    analysis {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(uuid.uuid4()),
                    "name": "YOLO",
                }
            },
        )

        self.assertEqual(
            {"success": False, "analysis": None, "errors": ["NOT_FOUND"]},
            r["data"]["updateAccessmodAccessibilityAnalysis"],
        )

    def test_update_accessmod_accessibility_analysis_null_fileset(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation updateAccessmodAccessibilityAnalysis($input: UpdateAccessmodAccessibilityAnalysisInput) {
                  updateAccessmodAccessibilityAnalysis(input: $input) {
                    success
                    analysis {
                        id
                        stack {
                            id
                        }
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                    "stackId": None,
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "analysis": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                    "stack": None,
                },
                "errors": [],
            },
            r["data"]["updateAccessmodAccessibilityAnalysis"],
        )

    def test_create_accessmod_zonal_statistics_analysis(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation createAccessmodZonalStatistics($input: CreateAccessmodZonalStatisticsInput) {
                  createAccessmodZonalStatistics(input: $input) {
                    success
                    analysis {
                        id
                        name
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "name": "A new ZonalStatistics analysis",
                }
            },
        )

        self.assertEqual(r["data"]["createAccessmodZonalStatistics"]["success"], True)
        self.assertEqual(
            r["data"]["createAccessmodZonalStatistics"]["analysis"]["name"],
            "A new ZonalStatistics analysis",
        )
        self.assertIsInstance(
            r["data"]["createAccessmodZonalStatistics"]["analysis"]["name"], str
        )
        self.assertEqual([], r["data"]["createAccessmodZonalStatistics"]["errors"])

    def test_create_accessmod_zonal_statistics_analysis_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation createAccessmodZonalStatistics($input: CreateAccessmodZonalStatisticsInput) {
                  createAccessmodZonalStatistics(input: $input) {
                    success
                    analysis {
                        id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "projectId": str(self.SAMPLE_PROJECT.id),
                    "name": self.ZONAL_STATISTICS_ANALYSIS_1.name,
                }
            },
        )

        self.assertEqual(
            {"success": False, "analysis": None, "errors": ["NAME_DUPLICATE"]},
            r["data"]["createAccessmodZonalStatistics"],
        )

    def test_update_accessmod_zonal_statistics_analysis(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation updateAccessmodZonalStatistics($input: UpdateAccessmodZonalStatisticsInput) {
                  updateAccessmodZonalStatistics(input: $input) {
                    success
                    analysis {
                        id
                        name
                        status
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ZONAL_STATISTICS_ANALYSIS_1.id),
                    "name": "Updated analysis!",
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "analysis": {
                    "id": str(self.ZONAL_STATISTICS_ANALYSIS_1.id),
                    "name": "Updated analysis!",
                    "status": AnalysisStatus.DRAFT,
                },
                "errors": [],
            },
            r["data"]["updateAccessmodZonalStatistics"],
        )

        r = self.run_query(
            """
                mutation updateAccessmodZonalStatistics($input: UpdateAccessmodZonalStatisticsInput) {
                  updateAccessmodZonalStatistics(input: $input) {
                    success
                    analysis {
                        status
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ZONAL_STATISTICS_ANALYSIS_1.id),
                    "name": "Updated analysis!",
                    "populationId": str(self.POPULATION_FILESET.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "analysis": {"status": AnalysisStatus.READY},
                "errors": [],
            },
            r["data"]["updateAccessmodZonalStatistics"],
        )

    @responses.activate
    def test_launch_accessmod_analysis(self):
        mock_raw_token = str(uuid.uuid4())
        mock_signed_token = Signer().sign_object(mock_raw_token)

        responses.add(
            responses.POST,
            urljoin(
                self.CLUSTER.api_url, f"dags/{self.DAG_ACCESSIBILITY.dag_id}/dagRuns"
            ),
            json={
                "conf": {},
                "dag_id": "am_accessibility_full",
                "dag_run_id": "am_accessibility_full_run_1",
                "end_date": "2021-10-09T16:42:16.189200+00:00",
                "execution_date": "2021-10-09T16:41:00+00:00",
                "external_trigger": False,
                "start_date": "2021-10-09T16:42:00.830209+00:00",
                "state": "queued",
            },
            # match=[
            #     matchers.json_params_matcher(
            #         {
            #             "conf": {
            #                 "output_dir": output_dir,
            #                 "algorithm": "ANISOTROPIC",
            #                 # "category_column": "???",   # TODO: add
            #                 "max_travel_time": 42,
            #                 "water_all_touched": True,
            #                 "knight_move": False,
            #                 "invert_direction": False,
            #                 "overwrite": False,
            #                 "_report_email": "jim@bluesquarehub.com",
            #                 "_webhook_token": mock_signed_token,
            #                 "_webhook_url": "http://app.openhexa.test/accessmod/webhook/",
            #             },
            #             "execution_date": "2022-03-01T11:19:29.730028+00:00",
            #         }
            #     )
            # ],
            status=200,
        )

        self.client.force_login(self.USER_1)
        with patch(
            "hexa.plugins.connector_airflow.models.DAG.build_webhook_token",
            return_value=(mock_raw_token, mock_signed_token),
        ):
            with patch(
                "django.utils.timezone.now",
                return_value=parse_datetime("2022-03-01T11:19:29.730028+00:00"),
            ):
                r = self.run_query(
                    """
                        mutation launchAccessmodAnalysis($input: LaunchAccessmodAnalysisInput) {
                          launchAccessmodAnalysis(input: $input) {
                            success
                            analysis {
                                status
                            }
                            errors
                          }
                        }
                    """,
                    {
                        "input": {
                            "id": str(self.ACCESSIBILITY_ANALYSIS_2.id),
                        }
                    },
                )

        self.assertEqual(
            {
                "success": True,
                "analysis": {"status": AnalysisStatus.QUEUED},
                "errors": [],
            },
            r["data"]["launchAccessmodAnalysis"],
        )

        self.assertEqual(1, self.DAG_ACCESSIBILITY.dagrun_set.count())
        dag_run = self.DAG_ACCESSIBILITY.dagrun_set.get()
        self.assertEqual(DAGRunState.QUEUED, dag_run.state)

    def test_launch_accessmod_analysis_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation launchAccessmodAnalysis($input: LaunchAccessmodAnalysisInput) {
                  launchAccessmodAnalysis(input: $input) {
                    success
                    analysis {
                      id
                    }
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": False,
                "analysis": {"id": str(self.ACCESSIBILITY_ANALYSIS_1.id)},
                "errors": ["LAUNCH_FAILED"],
            },
            r["data"]["launchAccessmodAnalysis"],
        )

    def test_delete_accessmod_analysis(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation deleteAccessmodAnalysis($input: DeleteAccessmodAnalysisInput) {
                  deleteAccessmodAnalysis(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                }
            },
        )

        self.assertEqual(
            {"success": True, "errors": []},
            r["data"]["deleteAccessmodAnalysis"],
        )

    def test_delete_accessmod_analysis_errors(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation deleteAccessmodAnalysis($input: DeleteAccessmodAnalysisInput) {
                  deleteAccessmodAnalysis(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(uuid.uuid4()),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["NOT_FOUND"]},
            r["data"]["deleteAccessmodAnalysis"],
        )

        r = self.run_query(
            """
                mutation deleteAccessmodAnalysis($input: DeleteAccessmodAnalysisInput) {
                  deleteAccessmodAnalysis(input: $input) {
                    success
                    errors
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.id),
                }
            },
        )

        self.assertEqual(
            {"success": False, "errors": ["DELETE_FAILED"]},
            r["data"]["deleteAccessmodAnalysis"],
        )

    def test_delete_accessmod_running_analysis(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation deleteAccessmodAnalysis($input: DeleteAccessmodAnalysisInput) {
                  deleteAccessmodAnalysis(input: $input) {
                    success
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.id),
                }
            },
        )

        self.assertEqual(
            {"success": False},
            r["data"]["deleteAccessmodAnalysis"],
        )
