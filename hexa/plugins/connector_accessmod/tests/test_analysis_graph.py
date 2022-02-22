from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
    AnalysisStatus,
    Fileset,
    FilesetFormat,
    FilesetRole,
    FilesetRoleCode,
    GeographicCoverageAnalysis,
    Project,
)
from hexa.user_management.models import User


class AccessmodAnalysisGraphTest(GraphQLTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.USER_1 = User.objects.create_user(
            "jim@bluesquarehub.com",
            "jimrocks",
        )
        cls.USER_2 = User.objects.create_user(
            "jane@bluesquarehub.com",
            "janerocks",
        )
        cls.SAMPLE_PROJECT = Project.objects.create(
            name="Sample project",
            country="BE",
            owner=cls.USER_1,
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
        cls.EXTENT_FILESET = Fileset.objects.create(
            name="Extent fileset",
            role=cls.GEOMETRY_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.LAND_COVER_FILESET = Fileset.objects.create(
            name="An impressive land cover",
            role=cls.LAND_COVER_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.DEM_FILESET = Fileset.objects.create(
            name="My favourite DEM",
            role=cls.DEM_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.TRANSPORT_NETWORK_FILESET = Fileset.objects.create(
            name="Worst Transport Network ever",
            role=cls.TRANSPORT_NETWORK_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.SLOPE_FILESET = Fileset.objects.create(
            name="A beautiful slope",
            role=cls.SLOPE_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.WATER_FILESET = Fileset.objects.create(
            name="I like water",
            role=cls.WATER_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.HEALTH_FACILITIES_FILESET = Fileset.objects.create(
            name="Would you look at those health facilities!",
            role=cls.HEALTH_FACILITIES_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.FRICTION_SURFACE_FILESET = Fileset.objects.create(
            name="Check this friction surface!",
            role=cls.FRICTION_SURFACE_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.POPULATION_FILESET = Fileset.objects.create(
            name="Best population ever",
            role=cls.POPULATION_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            owner=cls.USER_1,
            project=cls.SAMPLE_PROJECT,
            name="First accessibility analysis",
            slope=cls.SLOPE_FILESET,
        )
        cls.GEOGRAPHIC_COVERAGE_ANALYSIS = GeographicCoverageAnalysis.objects.create(
            owner=cls.USER_1,
            project=cls.SAMPLE_PROJECT,
            name="First Geo coverage analysis",
            population=cls.POPULATION_FILESET,
            friction_surface=cls.FRICTION_SURFACE_FILESET,
            dem=cls.DEM_FILESET,
            health_facilities=cls.HEALTH_FACILITIES_FILESET,
            hf_processing_order="plop",
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
                    ... on AccessmodAccessibilityAnalysis {
                        slope {
                            id
                        }
                    }
                  }
                }
            """,
            {"id": str(self.ACCESSIBILITY_ANALYSIS.id)},
        )

        self.assertEqual(
            r["data"]["accessmodAnalysis"],
            {
                "id": str(self.ACCESSIBILITY_ANALYSIS.id),
                "type": self.ACCESSIBILITY_ANALYSIS.type,
                "status": self.ACCESSIBILITY_ANALYSIS.status,
                "name": self.ACCESSIBILITY_ANALYSIS.name,
                "slope": {"id": str(self.ACCESSIBILITY_ANALYSIS.slope.id)},
            },
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
            {"id": str(self.ACCESSIBILITY_ANALYSIS.id)},
        )

        self.assertEqual(
            r["data"]["accessmodAnalysis"],
            None,
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
                "totalItems": 2,
                "items": [
                    {
                        "id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS.id),
                        "type": self.GEOGRAPHIC_COVERAGE_ANALYSIS.type,
                        "frictionSurface": {
                            "id": str(
                                self.GEOGRAPHIC_COVERAGE_ANALYSIS.friction_surface.id
                            )
                        },
                    },
                    {
                        "id": str(self.ACCESSIBILITY_ANALYSIS.id),
                        "type": self.ACCESSIBILITY_ANALYSIS.type,
                        "slope": {"id": str(self.ACCESSIBILITY_ANALYSIS.slope.id)},
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
                "totalItems": 2,
                "items": [
                    {"id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS.id)},
                    {"id": str(self.ACCESSIBILITY_ANALYSIS.id)},
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
                "totalItems": 2,
                "items": [
                    {
                        "name": self.GEOGRAPHIC_COVERAGE_ANALYSIS.name,
                    },
                    {
                        "name": self.ACCESSIBILITY_ANALYSIS.name,
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
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS.id),
                    "name": "Updated accessibility analysis!",
                    "slopeId": str(self.SLOPE_FILESET.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "analysis": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS.id),
                    "name": "Updated accessibility analysis!",
                    "status": AnalysisStatus.DRAFT,
                },
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
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS.id),
                    "name": "Updated accessibility analysis!",
                    "extentId": str(self.EXTENT_FILESET.id),
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
            },
        )

    def test_launch_accessmod_ready_analysis(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation launchAccessmodAnalysis($input: LaunchAccessmodAnalysisInput) {
                  launchAccessmodAnalysis(input: $input) {
                    success
                    analysis {
                        status
                    }
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS.id),
                }
            },
        )

        self.assertEqual(
            {"success": True, "analysis": {"status": AnalysisStatus.QUEUED}},
            r["data"]["launchAccessmodAnalysis"],
        )

    def test_launch_accessmod_draft_analysis(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                mutation launchAccessmodAnalysis($input: LaunchAccessmodAnalysisInput) {
                  launchAccessmodAnalysis(input: $input) {
                    success
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS.id),
                }
            },
        )

        self.assertEqual(
            {"success": False},
            r["data"]["launchAccessmodAnalysis"],
        )
