from hexa.core.test import GraphQLTestCase
from hexa.plugins.connector_accessmod.models import (
    AccessibilityAnalysis,
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
        cls.ACCESSIBILITY_ANALYSIS = AccessibilityAnalysis.objects.create(
            name="First accessibility analysis",
        )
        cls.GEOGRAPHIC_COVERAGE_ANALYSIS = GeographicCoverageAnalysis.objects.create(
            name="First Geo coverage analysis",
        )

    def test_accessmod_analysis_owner(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodAnalysis($id: String!) {
                  accessmodAnalysis(id: $id) {
                    id
                    name
                    status
                    ... on AccessModAccessibilityAnalysis {
                        slope
                    }
                  }
                }
            """,
            {"id": str(self.ACCESSIBILITY_ANALYSIS.id)},
        )

        self.assertEqual(
            r["data"]["accessmodAnalysis"],
            {
                "id": str(self.SAMPLE_PROJECT.id),
                "name": "Sample project",
                "status": "some status",
                "slope": "some slope",
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
                query accessmodAnalyses {
                  accessmodAnalyses {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodProjects"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.ACCESSIBILITY_ANALYSIS.id)},
                    {"id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS.id)},
                ],
            },
        )

    def test_accessmod_analyses_with_pagination(self):
        self.client.force_login(self.USER_1)

        r = self.run_query(
            """
                query accessmodAnalyses {
                  accessmodAnalyses(page: 1, perPage: 10) {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
        )

        self.assertEqual(
            r["data"]["accessmodAnalyses"],
            {
                "pageNumber": 1,
                "totalPages": 1,
                "totalItems": 2,
                "items": [
                    {"id": str(self.ACCESSIBILITY_ANALYSIS.id)},
                    {"id": str(self.GEOGRAPHIC_COVERAGE_ANALYSIS.id)},
                ],
            },
        )

    def test_accessmod_analyses_empty(self):
        self.client.force_login(self.USER_2)

        r = self.run_query(
            """
                query accessmodAnalyses {
                  accessmodAnalyses {
                    pageNumber
                    totalPages
                    totalItems
                    items {
                      id
                    }
                  }
                }
            """,
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
                        name
                        slope
                    }
                  }
                }
            """,
            {
                "input": {
                    "name": "My new project",
                    "spatialResolution": 42,
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["createAccessmodAccessibilityAnalysis"],
            {
                "success": True,
                "project": {
                    "name": "My new project",
                    "spatialResolution": 42,
                    "country": {"code": "CD"},
                },
            },
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
                        slope
                    }
                  }
                }
            """,
            {
                "input": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": "Updated project!",
                    "country": {"code": "CD"},
                }
            },
        )

        self.assertEqual(
            r["data"]["updateAccessmodAccessibilityAnalysis"],
            {
                "success": True,
                "project": {
                    "id": str(self.SAMPLE_PROJECT.id),
                    "name": "Updated project!",
                    "country": {"code": "CD"},
                },
            },
        )
