import uuid
from unittest import skip
from unittest.mock import patch
from urllib.parse import urljoin

import responses
from django.conf import settings
from django.core.signing import Signer
from django.utils.dateparse import parse_datetime
from responses import matchers

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    AccessibilityAnalysisAlgorithm,
    AnalysisStatus,
    File,
    Fileset,
    FilesetFormat,
    FilesetRole,
    FilesetRoleCode,
    GeographicCoverageAnalysis,
    Project,
)
from hexa.plugins.connector_airflow.models import DAG, Cluster, DAGRunState, DAGTemplate
from hexa.plugins.connector_s3.models import Bucket
from hexa.user_management.models import User


class AccessmodAnalysisGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_1 = User.objects.create_user(
            "jim@bluesquarehub.com", "jimrocks", is_superuser=True
        )
        cls.USER_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks",
        )
        cls.BUCKET = Bucket.objects.create(name=settings.ACCESSMOD_S3_BUCKET_NAME)
        cls.CLUSTER = Cluster.objects.create(
            name="test_cluster", url="https://lookimacluster.com/api"
        )
        cls.DAG_TEMPLATE = DAGTemplate.objects.create(
            cluster=cls.CLUSTER,
            code="AM_ACCESSIBILITY",
            description="AccessMod accessibility Analysis",
            sample_config={"foo": "bar"},
        )
        cls.DAG = DAG.objects.create(
            template=cls.DAG_TEMPLATE,
            dag_id="am_accessibility",
        )

        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="BE",
            author=cls.USER_1,
            spatial_resolution=100,
            crs=4326,
        )
        cls.GEOMETRY_ROLE = FilesetRole.objects.create(
            name="Geometry",
            code=FilesetRoleCode.GEOMETRY,
            format=FilesetFormat.VECTOR,
        )
        cls.LAND_COVER_ROLE = FilesetRole.objects.create(
            name="Land Cover",
            code=FilesetRoleCode.LAND_COVER,
            format=FilesetFormat.RASTER,
        )
        cls.DEM_ROLE = FilesetRole.objects.create(
            name="Digital Elevation Model",
            code=FilesetRoleCode.DEM,
            format=FilesetFormat.RASTER,
        )
        cls.TRANSPORT_NETWORK_ROLE = FilesetRole.objects.create(
            name="Transport Network",
            code=FilesetRoleCode.TRANSPORT_NETWORK,
            format=FilesetFormat.VECTOR,
        )
        cls.SLOPE_ROLE = FilesetRole.objects.create(
            name="Slope",
            code=FilesetRoleCode.SLOPE,
            format=FilesetFormat.RASTER,
        )
        cls.WATER_ROLE = FilesetRole.objects.create(
            name="Water",
            code=FilesetRoleCode.WATER,
            format=FilesetFormat.RASTER,
        )
        cls.HEALTH_FACILITIES_ROLE = FilesetRole.objects.create(
            name="Health Facilities",
            code=FilesetRoleCode.HEALTH_FACILITIES,
            format=FilesetFormat.VECTOR,
        )
        cls.FRICTION_SURFACE_ROLE = FilesetRole.objects.create(
            name="Friction surface",
            code=FilesetRoleCode.FRICTION_SURFACE,
            format=FilesetFormat.RASTER,
        )
        cls.POPULATION_ROLE = FilesetRole.objects.create(
            name="Population",
            code=FilesetRoleCode.POPULATION,
            format=FilesetFormat.RASTER,
        )
        cls.STACK_ROLE = FilesetRole.objects.create(
            name="Stack", code=FilesetRoleCode.STACK, format=FilesetFormat.RASTER
        )
        cls.EXTENT_FILESET = Fileset.objects.create(
            name="Extent fileset",
            role=cls.GEOMETRY_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
        )
        cls.LAND_COVER_FILESET = Fileset.objects.create(
            name="An impressive land cover",
            role=cls.LAND_COVER_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
        )
        cls.DEM_FILESET = Fileset.objects.create(
            name="My favorite DEM",
            role=cls.DEM_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
        )
        cls.TRANSPORT_NETWORK_FILESET = Fileset.objects.create(
            name="Worst Transport Network ever",
            role=cls.TRANSPORT_NETWORK_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
        )
        cls.SLOPE_FILESET = Fileset.objects.create(
            name="A beautiful slope",
            role=cls.SLOPE_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
        )
        cls.SLOPE_FILE = File.objects.create(
            fileset=cls.SLOPE_FILESET,
            uri=f"s3://{cls.BUCKET.name}/{cls.SAMPLE_PROJECT.id}/file_1.csv/",
            mime_type="text/csv",
        )
        cls.WATER_FILESET = Fileset.objects.create(
            name="I like water",
            role=cls.WATER_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
        )
        cls.HEALTH_FACILITIES_FILESET = Fileset.objects.create(
            name="Would you look at those health facilities!",
            role=cls.HEALTH_FACILITIES_ROLE,
            project=cls.SAMPLE_PROJECT,
            author=cls.USER_1,
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
            slope=cls.SLOPE_FILESET,
            dem=cls.STACK_FILESET,
        )
        cls.ACCESSIBILITY_ANALYSIS_2 = AccessibilityAnalysis.objects.create(
            author=cls.USER_1,
            project=cls.SAMPLE_PROJECT,
            name="Second accessibility analysis",
            status=AnalysisStatus.READY,  # let's cheat a little
            slope=cls.SLOPE_FILESET,
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

    @skip
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
                    slope {
                      id
                    }
                    water {
                      id
                    }
                    barrier {
                      id
                    }
                    movingSpeeds {
                      id
                    }
                    healthFacilities {
                      id
                    }
                    invertDirection
                    maxTravelTime
                    maxSlope
                    priorityRoads
                    priorityLandCover
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
                "stack": {"id": str(self.ACCESSIBILITY_ANALYSIS_1.stack.id)},
                "landCover": None,
                "dem": None,
                "transportNetwork": None,
                "slope": {"id": str(self.ACCESSIBILITY_ANALYSIS_1.slope.id)},
                "water": None,
                "barrier": None,
                "movingSpeeds": None,
                "healthFacilities": None,
                "invertDirection": False,
                "maxTravelTime": 360,
                "maxSlope": None,
                "priorityRoads": True,
                "priorityLandCover": [1, 2],
                "waterAllTouched": True,
                "algorithm": AccessibilityAnalysisAlgorithm.ANISOTROPIC,
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

    @skip
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
                            ... on AccessmodAccessibilityAnalysis {
                                slope {
                                    id
                                }
                            }
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
                "totalItems": 4,
                "items": [
                    {
                        "id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.id),
                        "type": self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.type,
                        "frictionSurface": {
                            "id": str(
                                self.GEOGRAPHIC_COVERAGE_ANALYSIS_2.friction_surface.id
                            )
                        },
                    },
                    {
                        "id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS_1.id),
                        "type": self.GEOGRAPHIC_COVERAGE_ANALYSIS_1.type,
                        "frictionSurface": {
                            "id": str(
                                self.GEOGRAPHIC_COVERAGE_ANALYSIS_1.friction_surface.id
                            )
                        },
                    },
                    {
                        "id": str(self.ACCESSIBILITY_ANALYSIS_2.id),
                        "type": self.ACCESSIBILITY_ANALYSIS_2.type,
                        "slope": {"id": str(self.ACCESSIBILITY_ANALYSIS_2.slope.id)},
                    },
                    {
                        "id": str(self.ACCESSIBILITY_ANALYSIS_1.id),
                        "type": self.ACCESSIBILITY_ANALYSIS_1.type,
                        "slope": {"id": str(self.ACCESSIBILITY_ANALYSIS_1.slope.id)},
                    },
                ],
            },
        )

    @skip
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
                "totalItems": 4,
                "items": [
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

    @skip
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
                "totalItems": 4,
                "items": [
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

    @skip
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

    @skip
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

    @skip
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
                    "slopeId": str(self.SLOPE_FILESET.id),
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
                    "slopeId": str(self.SLOPE_FILESET.id),
                    "waterId": str(self.WATER_FILESET.id),
                    "healthFacilitiesId": str(self.HEALTH_FACILITIES_FILESET.id),
                }
            },
        )

        self.assertEqual(
            r["data"]["updateAccessmodAccessibilityAnalysis"],
            {
                "success": True,
                "analysis": {"status": AnalysisStatus.READY},
                "errors": [],
            },
        )

    @skip
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

    @responses.activate
    @skip
    def test_launch_accessmod_analysis(self):
        mock_raw_token = str(uuid.uuid4())
        mock_signed_token = Signer().sign_object(mock_raw_token)

        output_dir = f"s3://{self.BUCKET.name}/{self.SAMPLE_PROJECT.id}/{self.ACCESSIBILITY_ANALYSIS_2.id}/"
        responses.add(
            responses.POST,
            urljoin(self.CLUSTER.api_url, f"dags/{self.DAG.dag_id}/dagRuns"),
            json={
                "conf": {},
                "dag_id": "am_accessibility",
                "dag_run_id": "am_accessibility_run_1",
                "end_date": "2021-10-09T16:42:16.189200+00:00",
                "execution_date": "2021-10-09T16:41:00+00:00",
                "external_trigger": False,
                "start_date": "2021-10-09T16:42:00.830209+00:00",
                "state": "queued",
            },
            match=[
                matchers.json_params_matcher(
                    {
                        "conf": {
                            "output_dir": output_dir,
                            "slope": self.SLOPE_FILESET.file_set.first().uri,
                            "algorithm": "ANISOTROPIC",
                            # "category_column": "???",   # TODO: add
                            "max_travel_time": 42,
                            "water_all_touched": True,
                            "knight_move": False,
                            "invert_direction": False,
                            "overwrite": False,
                            "_report_email": "jim@bluesquarehub.com",
                            "_webhook_token": mock_signed_token,
                            "_webhook_url": "http://app.openhexa.test/accessmod/webhook/",
                        },
                        "execution_date": "2022-03-01T11:19:29.730028+00:00",
                    }
                )
            ],
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

        self.assertEqual(1, self.DAG.dagrun_set.count())
        dag_run = self.DAG.dagrun_set.get()
        self.assertEqual(DAGRunState.QUEUED, dag_run.state)

    @skip
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

    @skip
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

    @skip
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
