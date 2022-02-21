from unittest import skip

from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
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
        )
        cls.SLOPE_ROLE = FilesetRole.objects.create(
            name="Slope",
            code=FilesetRoleCode.SLOPE,
            format=FilesetFormat.RASTER,
        )
        cls.FRICTION_SURFACE_ROLE = FilesetRole.objects.create(
            name="Friction surface",
            code=FilesetRoleCode.FRICTION_SURFACE,
            format=FilesetFormat.RASTER,
        )
        cls.SLOPE_FILESET = Fileset.objects.create(
            name="A beautiful slope",
            role=cls.SLOPE_ROLE,
            project=cls.SAMPLE_PROJECT,
            owner=cls.USER_1,
        )
        cls.FRICTION_SURFACE_FILESET = Fileset.objects.create(
            name="Check this friction surface!",
            role=cls.FRICTION_SURFACE_ROLE,
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
            friction_surface=cls.FRICTION_SURFACE_FILESET,
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
                    }
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS.id),
                    "name": "Updated accessibility analysis!",
                }
            },
        )

        self.assertEqual(
            r["data"]["updateAccessmodAccessibilityAnalysis"],
            {
                "success": True,
                "analysis": {
                    "id": str(self.ACCESSIBILITY_ANALYSIS.id),
                    "name": "Updated accessibility analysis!",
                },
            },
        )
