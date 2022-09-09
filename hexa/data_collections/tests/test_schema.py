from hexa.core.test import GraphQLTestCase
from hexa.data_collections.models import Collection
from hexa.user_management.models import Membership, Team, User
from hexa.visualizations.models import ExternalDashboard, ExternalDashboardPermission


class CollectionTest(GraphQLTestCase):
    USER_SABRINA = None
    USER_REBECCA = None

    @classmethod
    def setUpTestData(cls):
        cls.TEAM = Team.objects.create(name="Test Team")
        cls.USER_SABRINA = User.objects.create_user(
            "sabrina@bluesquarehub.com",
            "standardpassword",
        )
        Membership.objects.create(user=cls.USER_SABRINA, team=cls.TEAM)
        cls.USER_REBECCA = User.objects.create_user(
            "rebecca@bluesquarehub.com",
            "standardpassword",
        )
        cls.COLLECTION = Collection.objects.create(
            name="Malaria in RDC", author=cls.USER_SABRINA
        )
        cls.VIZ = ExternalDashboard.objects.create(
            url="https://viz.url", picture="__OVERRIDE_TEST__"
        )

        ExternalDashboardPermission.objects.create(
            external_dashboard=cls.VIZ, team=cls.TEAM
        )

    def test_create_collection(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation createCollection($input: CreateCollectionInput!) {
                createCollection(input: $input) {
                    success
                    errors
                    collection {
                        name
                        summary
                        description
                        countries {
                            code
                        }
                    }
                }
            }
          """,
            {
                "input": {
                    "name": "Created Collection",
                    "summary": "Collection summary",
                    "description": "Collection description",
                    "countries": [{"code": "BE"}],
                }
            },
        )

        self.assertTrue(
            r["data"]["createCollection"]["success"],
        )
        self.assertEqual(
            {
                "name": "Created Collection",
                "summary": "Collection summary",
                "description": "Collection description",
                "countries": [{"code": "BE"}],
            },
            r["data"]["createCollection"]["collection"],
        )

    def test_delete_collection(self):
        self.client.force_login(self.USER_SABRINA)
        r = self.run_query(
            """
            mutation deleteCollection($input: DeleteCollectionInput!) {
                deleteCollection(input: $input) {
                    success
                    errors
                }
            }
          """,
            {
                "input": {
                    "id": str(self.COLLECTION.id),
                }
            },
        )

        self.assertEqual({"success": True, "errors": []}, r["data"]["deleteCollection"])
        self.assertEqual(
            False, Collection.objects.filter(id=self.COLLECTION.id).exists()
        )

    def test_create_delete_collection_element(self):
        self.client.force_login(self.USER_SABRINA)

        r = self.run_query(
            """
            mutation createCollectionElement($input: CreateCollectionElementInput!) {
                createCollectionElement(input: $input) {
                    success
                    errors
                    element {
                        app
                        model
                        type
                        objectId
                        url
                        name
                    }
                }
            }
          """,
            {
                "input": {
                    "app": "visualizations",
                    "model": "externaldashboard",
                    "objectId": str(self.VIZ.id),
                    "collectionId": str(self.COLLECTION.id),
                }
            },
        )

        self.assertEqual(
            {
                "success": True,
                "errors": [],
                "element": {
                    "name": self.VIZ.index.display_name,
                    "app": "visualizations",
                    "model": "externaldashboard",
                    "objectId": str(self.VIZ.id),
                    "type": "external dashboard",
                    "url": "https://viz.url",
                },
            },
            r["data"]["createCollectionElement"],
        )
        self.assertEqual(1, self.COLLECTION.elements.count())

        r = self.run_query(
            """
            mutation deleteCollectionElement($input: DeleteCollectionElementInput!) {
                deleteCollectionElement(input: $input) {
                    success
                    errors
                }
            }
          """,
            {"input": {"id": str(self.COLLECTION.elements.first().id)}},
        )
        self.assertEqual(
            {"success": True, "errors": []}, r["data"]["deleteCollectionElement"]
        )
        self.assertEqual(0, self.COLLECTION.elements.count())
